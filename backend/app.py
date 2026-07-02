import os
import json
import calendar
from datetime import date, timedelta

# Load .env file automatically (GA_PROPERTY_ID, GSC_SITE_URL, FLASK_SECRET_KEY, etc.)
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass  # python-dotenv not installed; rely on system env vars
from collections import defaultdict
from flask import Flask, jsonify, request, redirect, session
from flask_cors import CORS

# ── Google Analytics Data SDK ──────────────────────────────────────────────────
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        RunReportRequest, DateRange, Dimension, Metric
    )
    GOOGLE_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_SDK_AVAILABLE = False

# ── OAuth (web flow, kept for future use) ─────────────────────────────────────
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
except ImportError:
    Credentials = None
    Flow = None

try:
    from googleapiclient.discovery import build
    GSC_SDK_AVAILABLE = True
except ImportError:
    build = None
    GSC_SDK_AVAILABLE = False

# ── Constants ─────────────────────────────────────────────────────────────────
GOOGLE_SCOPES       = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
TOKEN_FILE          = os.path.join(os.path.dirname(__file__), "token.json")
CREDENTIALS_PATH    = os.path.join(os.path.dirname(__file__), "service-account.json")
OAUTH_REDIRECT_URI  = "http://localhost:5000/api/auth/callback"

PROPERTY_ID   = os.environ.get("GA_PROPERTY_ID", "")
GSC_SITE_URL  = os.environ.get("GSC_SITE_URL", "")

# ── Flask app ─────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-in-production")
CORS(app, supports_credentials=True)
os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")


# ── Auth helpers ──────────────────────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "countries_config.json")

def load_countries_config():
    """Loads country-specific credentials and site configs."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading countries_config.json: {e}")
    return {}


def get_country_config(country_code="in"):
    """Gets the configuration dictionary for a given country, defaulting to India ('in')."""
    configs = load_countries_config()
    return configs.get(country_code, configs.get("in", {}))


def is_country_configured(country_code="in"):
    """Checks if the country is fully configured with credentials and property IDs."""
    config = get_country_config(country_code)
    property_id = config.get("ga_property_id", "")
    
    if not property_id or property_id.startswith("GA_PROPERTY_ID_"):
        return False
        
    cred_file = config.get("credentials_path", "service-account.json")
    if not os.path.pathsep in cred_file and not os.path.isabs(cred_file):
        cred_file = os.path.join(os.path.dirname(__file__), cred_file)
        
    if not os.path.exists(cred_file):
        default_cred = os.path.join(os.path.dirname(__file__), "service-account.json")
        if not os.path.exists(default_cred):
            return False
            
    return True


def get_google_credentials(country_code="in"):
    """
    Returns Google OAuth credentials for Analytics + Search Console.
    Priority: country-specific service account -> default service-account.json -> token.json -> None
    """
    config = get_country_config(country_code)
    cred_file = config.get("credentials_path", "service-account.json")
    if not os.path.isabs(cred_file):
        cred_file = os.path.join(os.path.dirname(__file__), cred_file)

    if os.path.exists(cred_file):
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(
            cred_file, scopes=GOOGLE_SCOPES
        )

    # Fallback to default service account
    default_cred = os.path.join(os.path.dirname(__file__), "service-account.json")
    if os.path.exists(default_cred):
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(
            default_cred, scopes=GOOGLE_SCOPES
        )

    if os.path.exists(TOKEN_FILE) and Credentials:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, GOOGLE_SCOPES)
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        return creds

    return None


def get_ga4_client(country_code="in"):
    """Returns an authenticated BetaAnalyticsDataClient."""
    if not GOOGLE_SDK_AVAILABLE:
        return None
    creds = get_google_credentials(country_code)
    return BetaAnalyticsDataClient(credentials=creds) if creds else None


def get_gsc_service(country_code="in"):
    """Returns an authenticated Search Console API service."""
    if not GSC_SDK_AVAILABLE:
        return None
    creds = get_google_credentials(country_code)
    return build("searchconsole", "v1", credentials=creds) if creds else None


def month_date_range(month: str):
    """Returns (start_date, end_date) strings for a given 'YYYY-MM' month."""
    year, mo = map(int, month.split("-"))
    last_day = calendar.monthrange(year, mo)[1]
    return f"{month}-01", f"{month}-{last_day:02d}"


def gsc_date_range(month: str):
    """
    Returns (start_date, end_date) as YYYY-MM-DD for Search Console.
    GSC data lags ~3 days; end date is clamped accordingly.
    """
    gsc_latest = date.today() - timedelta(days=3)
    if month:
        start, end = month_date_range(month)
        end_date = min(date.fromisoformat(end), gsc_latest)
        if end_date < date.fromisoformat(start):
            return None, None
        return start, end_date.isoformat()
    start_date = gsc_latest - timedelta(days=27)
    return start_date.isoformat(), gsc_latest.isoformat()


def calculate_percent_change(current, previous):
    if not previous:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)


# ── Empty response shapes (used when GA4 is not configured) ───────────────────
EMPTY_SUMMARY = {
    "current": {
        "traffic": None,
        "leads": None,
        "chatbotQueries": None,
        "conversionRate": None
    },
    "change": {
        "traffic": None,
        "leads": None,
        "chatbotQueries": None,
        "conversionRate": None
    },
    "source": "unavailable"
}


# ─────────────────────────────────────────────────────────────────────────────
# OAuth routes (kept for future manual auth)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/auth/google", methods=["GET"])
def google_oauth():
    if Flow is None:
        return jsonify({"error": "google-auth-oauthlib not installed"}), 500
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=GOOGLE_SCOPES, redirect_uri=OAUTH_REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", prompt="consent"
    )
    session["oauth_state"] = state
    return redirect(auth_url)


@app.route("/api/auth/callback", methods=["GET"])
def oauth_callback():
    if Flow is None:
        return jsonify({"error": "google-auth-oauthlib not installed"}), 500
    state = session.get("oauth_state")
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=GOOGLE_SCOPES,
        state=state, redirect_uri=OAUTH_REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)
    with open(TOKEN_FILE, "w") as f:
        f.write(flow.credentials.to_json())
    return """
    <html><body style="font-family:sans-serif;text-align:center;margin-top:80px">
      <h2>&#x2705; Google Analytics &amp; Search Console connected!</h2>
      <p>token.json saved. Restart the Flask server.</p>
    </body></html>
    """


# ─────────────────────────────────────────────────────────────────────────────
# Diagnostic
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/ga4/status", methods=["GET"])
def ga4_status():
    client = get_ga4_client()
    if not client:
        return jsonify({
            "connected": False,
            "reason": "No credentials found (service-account.json or token.json missing)"
        })
    if not PROPERTY_ID:
        return jsonify({
            "connected": True, "credentials": "ok", "property_id": None,
            "reason": "Credentials OK but GA_PROPERTY_ID env var not set."
        })
    try:
        req = RunReportRequest(
            property=f"properties/{PROPERTY_ID}",
            metrics=[Metric(name="activeUsers")],
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
        )
        resp = client.run_report(req)
        users = int(resp.rows[0].metric_values[0].value) if resp.rows else 0
        return jsonify({
            "connected": True, "property_id": PROPERTY_ID,
            "test_metric": {"activeUsers_last7days": users}
        })
    except Exception as e:
        return jsonify({"connected": False, "property_id": PROPERTY_ID, "error": str(e)})


# ─────────────────────────────────────────────────────────────────────────────
# 1. Summary metrics
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics/summary", methods=["GET"])
def get_summary():
    month = request.args.get("month", "")
    country = request.args.get("country", "in")

    if not is_country_configured(country):
        return jsonify(EMPTY_SUMMARY)

    client = get_ga4_client(country)
    config = get_country_config(country)
    property_id = config.get("ga_property_id", "")

    if not client or not property_id:
        return jsonify(EMPTY_SUMMARY)

    try:
        start, end = month_date_range(month) if month else ("30daysAgo", "today")

        # Current period
        req = RunReportRequest(
            property=f"properties/{property_id}",
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="sessions"),
                Metric(name="conversions"),
                Metric(name="bounceRate"),
            ],
            date_ranges=[DateRange(start_date=start, end_date=end)],
        )
        resp = client.run_report(req)
        row = resp.rows[0] if resp.rows else None

        traffic         = int(row.metric_values[0].value) if row else 0
        sessions        = int(row.metric_values[1].value) if row else 0
        conversions     = int(row.metric_values[2].value) if row else 0
        bounce_rate     = round(float(row.metric_values[3].value) * 100, 2) if row else 0.0

        # Previous period for change %
        prev_traffic = prev_sessions = prev_conversions = 0
        if month:
            year, mo = map(int, month.split("-"))
            prev_mo = mo - 1
            prev_year = year
            if prev_mo == 0:
                prev_mo = 12
                prev_year -= 1
            prev_start = f"{prev_year}-{prev_mo:02d}-01"
            prev_last  = calendar.monthrange(prev_year, prev_mo)[1]
            prev_end   = f"{prev_year}-{prev_mo:02d}-{prev_last:02d}"

            prev_req = RunReportRequest(
                property=f"properties/{property_id}",
                metrics=[
                    Metric(name="activeUsers"),
                    Metric(name="sessions"),
                    Metric(name="conversions"),
                ],
                date_ranges=[DateRange(start_date=prev_start, end_date=prev_end)],
            )
            prev_resp = client.run_report(prev_req)
            if prev_resp.rows:
                pr = prev_resp.rows[0]
                prev_traffic     = int(pr.metric_values[0].value)
                prev_sessions    = int(pr.metric_values[1].value)
                prev_conversions = int(pr.metric_values[2].value)

        return jsonify({
            "current": {
                "traffic": traffic,
                "leads": conversions,
                "chatbotQueries": sessions,
                "conversionRate": bounce_rate
            },
            "change": {
                "traffic":        calculate_percent_change(traffic, prev_traffic),
                "leads":          calculate_percent_change(conversions, prev_conversions),
                "chatbotQueries": calculate_percent_change(sessions, prev_sessions),
                "conversionRate": 0.0
            },
            "source": "live"
        })
    except Exception as e:
        print(f"GA4 summary error: {e}")
        return jsonify(EMPTY_SUMMARY)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Top pages
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics/top-pages", methods=["GET"])
def get_top_pages():
    month = request.args.get("month", "")
    country = request.args.get("country", "in")

    if not is_country_configured(country):
        return jsonify([])

    client = get_ga4_client(country)
    config = get_country_config(country)
    property_id = config.get("ga_property_id", "")

    if not client or not property_id:
        return jsonify([])

    try:
        start, end = month_date_range(month) if month else ("30daysAgo", "today")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="screenPageViews"), Metric(name="bounceRate")],
            date_ranges=[DateRange(start_date=start, end_date=end)],
            limit=10,
        )
        resp = client.run_report(req)
        return jsonify([
            {
                "url":        row.dimension_values[0].value,
                "views":      int(row.metric_values[0].value),
                "bounceRate": round(float(row.metric_values[1].value) * 100, 1)
            }
            for row in resp.rows
        ])
    except Exception as e:
        print(f"GA4 top-pages error: {e}")
        return jsonify([])


# ─────────────────────────────────────────────────────────────────────────────
# 3. User flow
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics/user-flow", methods=["GET"])
def get_user_flow():
    month = request.args.get("month", "")
    country = request.args.get("country", "in")

    if not is_country_configured(country):
        return jsonify([])

    client = get_ga4_client(country)
    config = get_country_config(country)
    property_id = config.get("ga_property_id", "")

    if not client or not property_id:
        return jsonify([])

    try:
        start, end = month_date_range(month) if month else ("30daysAgo", "today")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="pagePath")],
            metrics=[Metric(name="sessions"), Metric(name="bounceRate")],
            date_ranges=[DateRange(start_date=start, end_date=end)],
            limit=4,
        )
        resp = client.run_report(req)
        flow = []
        for i, row in enumerate(resp.rows):
            page     = row.dimension_values[0].value
            sessions = int(row.metric_values[0].value)
            bounce   = round(float(row.metric_values[1].value) * 100, 1)
            flow.append({
                "stage":      f"{i + 1}. {page}",
                "page":       page,
                "visitors":   sessions,
                "dropoffRate": bounce
            })
        return jsonify(flow)
    except Exception as e:
        print(f"GA4 user-flow error: {e}")
        return jsonify([])


# ─────────────────────────────────────────────────────────────────────────────
# 4. Traffic trends
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics/traffic-trends", methods=["GET"])
def get_traffic_trends():
    month = request.args.get("month", "")
    country = request.args.get("country", "in")

    if not is_country_configured(country):
        return jsonify([])

    client = get_ga4_client(country)
    config = get_country_config(country)
    property_id = config.get("ga_property_id", "")

    if not client or not property_id:
        return jsonify([])

    try:
        start, end = month_date_range(month) if month else ("30daysAgo", "today")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="date"), Dimension(name="sessionDefaultChannelGroup")],
            metrics=[Metric(name="sessions")],
            date_ranges=[DateRange(start_date=start, end_date=end)],
        )
        resp = client.run_report(req)

        by_date = defaultdict(lambda: {"views": 0, "organic": 0, "direct": 0, "referral": 0})
        for row in resp.rows:
            d        = row.dimension_values[0].value          # YYYYMMDD from GA4
            channel  = row.dimension_values[1].value.lower()
            sessions = int(row.metric_values[0].value)
            by_date[d]["views"] += sessions
            if "organic" in channel:
                by_date[d]["organic"] += sessions
            elif "direct" in channel:
                by_date[d]["direct"] += sessions
            else:
                by_date[d]["referral"] += sessions

        from datetime import datetime
        return jsonify([
            {
                "date":     datetime.strptime(k, "%Y%m%d").strftime("%d %b %Y"),
                "views":    v["views"],
                "organic":  v["organic"],
                "direct":   v["direct"],
                "referral": v["referral"]
            }
            for k, v in sorted(by_date.items())
        ])
    except Exception as e:
        print(f"GA4 traffic-trends error: {e}")
        return jsonify([])



# ─────────────────────────────────────────────────────────────────────────────
# 5. SEO Performance  (Google Search Console Search Analytics API)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics/seo", methods=["GET"])
def get_seo():
    month = request.args.get("month", "")
    country = request.args.get("country", "in")

    if not is_country_configured(country):
        return jsonify({
            "score": None,
            "keywords": [],
            "note": f"Google Search Console credentials not configured for country: {country}",
        })

    service = get_gsc_service(country)
    config = get_country_config(country)
    gsc_site_url = config.get("gsc_site_url", "")

    if not service:
        return jsonify({
            "score": None,
            "keywords": [],
            "note": "No credentials found. Configure credentials in backend/countries_config.json.",
        })

    if not gsc_site_url:
        return jsonify({
            "score": None,
            "keywords": [],
            "note": "Set gsc_site_url in backend/countries_config.json.",
        })

    try:
        start_date, end_date = gsc_date_range(month)
        if not start_date:
            return jsonify({
                "score": None,
                "keywords": [],
                "note": "Search Console data is not yet available for this period.",
            })

        body = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": ["query"],
            "rowLimit": 10,
            "dataState": "final",
        }
        resp = service.searchanalytics().query(
            siteUrl=gsc_site_url, body=body
        ).execute()

        rows = resp.get("rows", [])
        keywords = [
            {
                "keyword": row["keys"][0],
                "position": round(row["position"], 1),
                "searches": int(row["impressions"]),
            }
            for row in rows
        ]

        score = None
        if keywords:
            total_impressions = sum(int(row["impressions"]) for row in rows)
            if total_impressions:
                weighted_pos = sum(
                    row["position"] * int(row["impressions"]) for row in rows
                ) / total_impressions
            else:
                weighted_pos = sum(k["position"] for k in keywords) / len(keywords)
            score = max(0, min(100, round(100 - (weighted_pos - 1) * 5)))

        return jsonify({"score": score, "keywords": keywords})

    except Exception as e:
        print(f"GSC SEO error: {e}")
        return jsonify({
            "score": None,
            "keywords": [],
            "note": f"Search Console error: {e}",
        })


# ─────────────────────────────────────────────────────────────────────────────
# 6. Page speed  (not available via GA4 Data API — requires PageSpeed Insights)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics/page-speed", methods=["GET"])
def get_page_speed():
    return jsonify({"score": None, "lcp": None, "fid": None, "cls": None,
                    "note": "Connect PageSpeed Insights API for live scores."})


# ─────────────────────────────────────────────────────────────────────────────
# 7. Form submissions / leads  (events from GA4)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics/form-submissions", methods=["GET"])
def get_form_submissions():
    month = request.args.get("month", "")
    country = request.args.get("country", "in")

    if not is_country_configured(country):
        return jsonify([])

    client = get_ga4_client(country)
    config = get_country_config(country)
    property_id = config.get("ga_property_id", "")

    if not client or not property_id:
        return jsonify([])

    try:
        start, end = month_date_range(month) if month else ("30daysAgo", "today")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="eventName"), Dimension(name="date")],
            metrics=[Metric(name="eventCount")],
            date_ranges=[DateRange(start_date=start, end_date=end)],
            limit=20,
        )
        resp = client.run_report(req)
        submissions = []
        for row in resp.rows:
            event = row.dimension_values[0].value
            if any(kw in event.lower() for kw in ["form", "submit", "lead", "contact", "inquiry"]):
                submissions.append({
                    "timestamp": row.dimension_values[1].value,
                    "source":    event,
                    "status":    "Received",
                    "count":     int(row.metric_values[0].value)
                })
        return jsonify(submissions)
    except Exception as e:
        print(f"GA4 form-submissions error: {e}")
        return jsonify([])


# ─────────────────────────────────────────────────────────────────────────────
# 8. Chatbot usage  (custom events from GA4)
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/api/analytics/chatbot", methods=["GET"])
def get_chatbot():
    month = request.args.get("month", "")
    country = request.args.get("country", "in")

    if not is_country_configured(country):
        return jsonify({"chatsInitiated": None, "resolutionRate": None, "avgResponseTime": None})

    client = get_ga4_client(country)
    config = get_country_config(country)
    property_id = config.get("ga_property_id", "")

    if not client or not property_id:
        return jsonify({"chatsInitiated": None, "resolutionRate": None, "avgResponseTime": None})

    try:
        start, end = month_date_range(month) if month else ("30daysAgo", "today")
        req = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="eventCount")],
            date_ranges=[DateRange(start_date=start, end_date=end)],
        )
        resp = client.run_report(req)
        chats = 0
        for row in resp.rows:
            event = row.dimension_values[0].value.lower()
            if "chat" in event or "bot" in event:
                chats += int(row.metric_values[0].value)
        return jsonify({
            "chatsInitiated":  chats if chats else None,
            "resolutionRate":  None,
            "avgResponseTime": None,
            "note":            "Track chatbot_open / chatbot_resolved events in GA4 for full metrics."
        })
    except Exception as e:
        print(f"GA4 chatbot error: {e}")
        return jsonify({"chatsInitiated": None, "resolutionRate": None, "avgResponseTime": None})


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sa_exists = os.path.exists(CREDENTIALS_PATH)
    tok_exists = os.path.exists(TOKEN_FILE)

    if GOOGLE_SDK_AVAILABLE and sa_exists:
        print(f"STATUS: ✅ Service account found → {CREDENTIALS_PATH}")
        if PROPERTY_ID:
            print(f"STATUS: ✅ GA4 Property ID = {PROPERTY_ID}")
            print("STATUS: Live data mode active. Check http://localhost:5000/api/ga4/status")
        else:
            print("STATUS: ⚠️  GA_PROPERTY_ID not set.")
            print("         Set it with:  $env:GA_PROPERTY_ID='YOUR_NUMERIC_PROPERTY_ID'")
            print("         Then restart Flask.")
    elif GOOGLE_SDK_AVAILABLE and tok_exists:
        print("STATUS: ✅ OAuth token found.")
        if not PROPERTY_ID:
            print("STATUS: ⚠️  GA_PROPERTY_ID not set.")
    else:
        print("STATUS: ⚠️  No credentials found. All endpoints return empty data.")

    if GSC_SITE_URL:
        print(f"STATUS: ✅ Search Console site = {GSC_SITE_URL}")
    else:
        print("STATUS: ⚠️  GSC_SITE_URL not set. SEO widget will show a setup message.")
        print("         Set it with:  $env:GSC_SITE_URL='https://www.yoursite.com/'")

    app.run(host="0.0.0.0", port=5000, debug=True)
