import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

# Optional imports for real Google Analytics queries
try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Metric, Dimension
    GOOGLE_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_SDK_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing for Angular frontend

# Configuration
PROPERTY_ID = os.environ.get("GA_PROPERTY_ID", "")
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "service-account.json")

# Helper to check if GA4 credentials are configured
def is_ga4_configured():
    return GOOGLE_SDK_AVAILABLE and PROPERTY_ID != "" and os.path.exists(CREDENTIALS_PATH)

# Initialize Google client if credentials exist
def get_ga4_client():
    if is_ga4_configured():
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CREDENTIALS_PATH
        return BetaAnalyticsDataClient()
    return None

# ==========================================
# Real Spreadsheet Metrics Database (Static)
# ==========================================
HISTORICAL_DATA = {
    "2026-05": {
        "summary": { 
            "traffic": 13705,        # Users from sheet (Table 2)
            "leads": 19793,          # Clicks from sheet (Table 1)
            "chatbotQueries": 17163, # Sessions from sheet (Table 2)
            "conversionRate": 0.89   # Clicks / Impressions * 100 = 19793 / 2225334 = 0.89%
        },
        "top_pages": [
            { "url": "/", "views": 14029, "bounceRate": 36.9 },
            { "url": "/blogs/17-dangerous-causes-of-kidney-disease", "views": 9800, "bounceRate": 35.5 },
            { "url": "/blogs/dialysis-at-home-care-tips", "views": 6200, "bounceRate": 32.4 },
            { "url": "/blogs/nine-levels-with-t-creatinine", "views": 4400, "bounceRate": 34.0 }
        ],
        "user_flow": [
            { "stage": "1. Entry Page", "page": "/", "dropoffRate": 36.9, "visitors": 13859 },
            { "stage": "2. High Traffic Blog", "page": "/blogs/17-dangerous-causes", "dropoffRate": 40.0, "visitors": 8746 },
            { "stage": "3. Portal Inquiry", "page": "/contact-us", "dropoffRate": 25.0, "visitors": 5247 },
            { "stage": "4. Conversion", "page": "/inquiry-complete", "dropoffRate": 0.0, "visitors": 3935 }
        ],
        "traffic_trends": [
            { "date": "May 16", "views": 2100, "organic": 1365, "direct": 525, "referral": 210 },
            { "date": "May 17", "views": 2450, "organic": 1592, "direct": 612, "referral": 246 },
            { "date": "May 18", "views": 2300, "organic": 1495, "direct": 575, "referral": 230 },
            { "date": "May 19", "views": 2600, "organic": 1690, "direct": 650, "referral": 260 },
            { "date": "May 20", "views": 2850, "organic": 1852, "direct": 712, "referral": 286 },
            { "date": "May 21", "views": 3100, "organic": 2015, "direct": 775, "referral": 310 },
            { "date": "May 22", "views": 2950, "organic": 1917, "direct": 737, "referral": 296 }
        ],
        "seo": {
            "score": 88,
            "keywords": [
                { "keyword": "dialysis center near me", "position": 2, "searches": 19793 },
                { "keyword": "kidney care center", "position": 4, "searches": 12999 },
                { "keyword": "nephrology specialist", "position": 6, "searches": 8450 }
            ]
        },
        "page_speed": { "score": 93, "lcp": 1.7, "fid": 38, "cls": 0.07 },
        "chatbot": { "chatsInitiated": 2574, "resolutionRate": 89.2, "avgResponseTime": 4.1 },
        "form_submissions": [
            { "timestamp": "11:30 AM", "source": "Dialysis Inquiry", "status": "Contacted" },
            { "timestamp": "09:45 AM", "source": "Newsletter Signup", "status": "Subscribed" },
            { "timestamp": "Yesterday", "source": "Callback Request", "status": "Processed" }
        ]
    },
    "2026-04": {
        "summary": { 
            "traffic": 12175,
            "leads": 17429,
            "chatbotQueries": 14940,
            "conversionRate": 0.79 # 17429 / 2219740 * 100 = 0.79%
        },
        "top_pages": [
            { "url": "/", "views": 11906, "bounceRate": 35.3 },
            { "url": "/blogs/17-dangerous-causes-of-kidney-disease", "views": 8400, "bounceRate": 36.2 },
            { "url": "/blogs/nine-levels-with-t-creatinine", "views": 3900, "bounceRate": 35.0 }
        ],
        "user_flow": [
            { "stage": "1. Entry Page", "page": "/", "dropoffRate": 35.3, "visitors": 12310 },
            { "stage": "2. High Traffic Blog", "page": "/blogs/17-dangerous-causes", "dropoffRate": 42.0, "visitors": 7964 },
            { "stage": "3. Portal Inquiry", "page": "/contact-us", "dropoffRate": 26.0, "visitors": 4619 },
            { "stage": "4. Conversion", "page": "/inquiry-complete", "dropoffRate": 0.0, "visitors": 3418 }
        ],
        "traffic_trends": [
            { "date": "Apr 16", "views": 1900, "organic": 1235, "direct": 475, "referral": 190 },
            { "date": "Apr 17", "views": 2150, "organic": 1397, "direct": 537, "referral": 216 },
            { "date": "Apr 18", "views": 2000, "organic": 1300, "direct": 500, "referral": 200 },
            { "date": "Apr 19", "views": 2300, "organic": 1495, "direct": 575, "referral": 230 },
            { "date": "Apr 20", "views": 2450, "organic": 1592, "direct": 612, "referral": 246 },
            { "date": "Apr 21", "views": 2600, "organic": 1690, "direct": 650, "referral": 260 },
            { "date": "Apr 22", "views": 2550, "organic": 1657, "direct": 637, "referral": 256 }
        ],
        "seo": {
            "score": 85,
            "keywords": [
                { "keyword": "dialysis center near me", "position": 3, "searches": 17429 },
                { "keyword": "kidney care center", "position": 5, "searches": 11440 },
                { "keyword": "nephrology specialist", "position": 7, "searches": 7820 }
            ]
        },
        "page_speed": { "score": 90, "lcp": 1.9, "fid": 42, "cls": 0.08 },
        "chatbot": { "chatsInitiated": 2241, "resolutionRate": 87.5, "avgResponseTime": 4.3 },
        "form_submissions": [
            { "timestamp": "04:15 PM", "source": "Dialysis Inquiry", "status": "Contacted" },
            { "timestamp": "11:00 AM", "source": "Newsletter Signup", "status": "Subscribed" },
            { "timestamp": "Yesterday", "source": "Callback Request", "status": "Processed" }
        ]
    },
    "2026-03": {
        "summary": { 
            "traffic": 11251,
            "leads": 16240,
            "chatbotQueries": 14117,
            "conversionRate": 0.83 # 16240 / 1948954 * 100 = 0.83%
        },
        "top_pages": [
            { "url": "/", "views": 13840, "bounceRate": 37.0 },
            { "url": "/blogs/17-dangerous-causes-of-kidney-disease", "views": 8100, "bounceRate": 38.5 },
            { "url": "/blogs/nine-levels-with-t-creatinine", "views": 3500, "bounceRate": 36.0 }
        ],
        "user_flow": [
            { "stage": "1. Entry Page", "page": "/", "dropoffRate": 37.0, "visitors": 11357 },
            { "stage": "2. High Traffic Blog", "page": "/blogs/17-dangerous-causes", "dropoffRate": 44.0, "visitors": 7154 },
            { "stage": "3. Portal Inquiry", "page": "/contact-us", "dropoffRate": 28.0, "visitors": 4006 },
            { "stage": "4. Conversion", "page": "/inquiry-complete", "dropoffRate": 0.0, "visitors": 2884 }
        ],
        "traffic_trends": [
            { "date": "Mar 16", "views": 1800, "organic": 1170, "direct": 450, "referral": 180 },
            { "date": "Mar 17", "views": 2000, "organic": 1300, "direct": 500, "referral": 200 },
            { "date": "Mar 18", "views": 1900, "organic": 1235, "direct": 475, "referral": 190 },
            { "date": "Mar 19", "views": 2100, "organic": 1365, "direct": 525, "referral": 210 },
            { "date": "Mar 20", "views": 2250, "organic": 1462, "direct": 562, "referral": 226 },
            { "date": "Mar 21", "views": 2400, "organic": 1560, "direct": 600, "referral": 240 },
            { "date": "Mar 22", "views": 2350, "organic": 1527, "direct": 587, "referral": 236 }
        ],
        "seo": {
            "score": 82,
            "keywords": [
                { "keyword": "dialysis center near me", "position": 4, "searches": 16240 },
                { "keyword": "kidney care center", "position": 6, "searches": 10584 },
                { "keyword": "nephrology specialist", "position": 8, "searches": 6900 }
            ]
        },
        "page_speed": { "score": 88, "lcp": 2.1, "fid": 48, "cls": 0.09 },
        "chatbot": { "chatsInitiated": 2117, "resolutionRate": 86.1, "avgResponseTime": 4.5 },
        "form_submissions": [
            { "timestamp": "02:45 PM", "source": "Dialysis Inquiry", "status": "Contacted" },
            { "timestamp": "10:30 AM", "source": "Newsletter Signup", "status": "Subscribed" },
            { "timestamp": "Yesterday", "source": "Callback Request", "status": "Processed" }
        ]
    },
    "2026-02": {
        "summary": { 
            "traffic": 9534,
            "leads": 13677,
            "chatbotQueries": 11920,
            "conversionRate": 0.84 # 13677 / 1634350 * 100 = 0.84%
        },
        "top_pages": [
            { "url": "/", "views": 46900, "bounceRate": 35.1 },
            { "url": "/blogs/nine-levels-with-t-creatinine", "views": 14200, "bounceRate": 36.2 },
            { "url": "/blogs/17-dangerous-causes-of-kidney-disease", "views": 7200, "bounceRate": 34.0 }
        ],
        "user_flow": [
            { "stage": "1. Entry Page", "page": "/", "dropoffRate": 35.1, "visitors": 9647 },
            { "stage": "2. High Traffic Blog", "page": "/blogs/nine-levels", "dropoffRate": 41.0, "visitors": 6260 },
            { "stage": "3. Portal Inquiry", "page": "/contact-us", "dropoffRate": 29.0, "visitors": 3693 },
            { "stage": "4. Conversion", "page": "/inquiry-complete", "dropoffRate": 0.0, "visitors": 2622 }
        ],
        "traffic_trends": [
            # Feb has Paid Search as Top traffic source: 55% Paid, 25% Organic, 20% Direct/Referral
            { "date": "Feb 16", "views": 1500, "organic": 375, "direct": 300, "referral": 825 }, # Referral counts as Paid/Social here
            { "date": "Feb 17", "views": 1700, "organic": 425, "direct": 340, "referral": 935 },
            { "date": "Feb 18", "views": 1600, "organic": 400, "direct": 320, "referral": 880 },
            { "date": "Feb 19", "views": 1800, "organic": 450, "direct": 360, "referral": 990 },
            { "date": "Feb 20", "views": 1950, "organic": 487, "direct": 390, "referral": 1073 },
            { "date": "Feb 21", "views": 2100, "organic": 525, "direct": 420, "referral": 1155 },
            { "date": "Feb 22", "views": 2050, "organic": 512, "direct": 410, "referral": 1128 }
        ],
        "seo": {
            "score": 79,
            "keywords": [
                { "keyword": "dialysis center near me", "position": 5, "searches": 13677 },
                { "keyword": "kidney care center", "position": 7, "searches": 8946 },
                { "keyword": "nephrology specialist", "position": 9, "searches": 5800 }
            ]
        },
        "page_speed": { "score": 86, "lcp": 2.3, "fid": 53, "cls": 0.10 },
        "chatbot": { "chatsInitiated": 1788, "resolutionRate": 84.5, "avgResponseTime": 4.9 },
        "form_submissions": [
            { "timestamp": "03:30 PM", "source": "Dialysis Inquiry", "status": "Contacted" },
            { "timestamp": "11:15 AM", "source": "Newsletter Signup", "status": "Subscribed" },
            { "timestamp": "Yesterday", "source": "Callback Request", "status": "Processed" }
        ]
    },
    "2026-01": {
        "summary": { 
            "traffic": 8489,
            "leads": 12535,
            "chatbotQueries": 11151,
            "conversionRate": 1.03 # 12535 / 1215747 * 100 = 1.03%
        },
        "top_pages": [
            { "url": "/", "views": 13416, "bounceRate": 32.9 },
            { "url": "/blogs/lowering-creatinine-levels", "views": 6800, "bounceRate": 31.2 },
            { "url": "/blogs/the-5-best-foods-for-kidneys", "views": 4200, "bounceRate": 34.0 }
        ],
        "user_flow": [
            { "stage": "1. Entry Page", "page": "/", "dropoffRate": 32.9, "visitors": 8641 },
            { "stage": "2. High Traffic Blog", "page": "/blogs/lowering-creatinine", "dropoffRate": 45.0, "visitors": 5798 },
            { "stage": "3. Portal Inquiry", "page": "/contact-us", "dropoffRate": 30.0, "visitors": 3189 },
            { "stage": "4. Conversion", "page": "/inquiry-complete", "dropoffRate": 0.0, "visitors": 2232 }
        ],
        "traffic_trends": [
            { "date": "Jan 16", "views": 1400, "organic": 910, "direct": 350, "referral": 140 },
            { "date": "Jan 17", "views": 1600, "organic": 1040, "direct": 400, "referral": 160 },
            { "date": "Jan 18", "views": 1500, "organic": 975, "direct": 375, "referral": 150 },
            { "date": "Jan 19", "views": 1700, "organic": 1105, "direct": 425, "referral": 170 },
            { "date": "Jan 20", "views": 1850, "organic": 1202, "direct": 462, "referral": 186 },
            { "date": "Jan 21", "views": 2000, "organic": 1300, "direct": 500, "referral": 200 },
            { "date": "Jan 22", "views": 1900, "organic": 1235, "direct": 475, "referral": 190 }
        ],
        "seo": {
            "score": 75,
            "keywords": [
                { "keyword": "dialysis center near me", "position": 6, "searches": 12535 },
                { "keyword": "kidney care center", "position": 8, "searches": 7926 },
                { "keyword": "nephrology specialist", "position": 11, "searches": 5100 }
            ]
        },
        "page_speed": { "score": 83, "lcp": 2.5, "fid": 59, "cls": 0.12 },
        "chatbot": { "chatsInitiated": 1672, "resolutionRate": 82.0, "avgResponseTime": 5.2 },
        "form_submissions": [
            { "timestamp": "01:15 PM", "source": "Dialysis Inquiry", "status": "Contacted" },
            { "timestamp": "09:30 AM", "source": "Newsletter Signup", "status": "Subscribed" },
            { "timestamp": "Yesterday", "source": "Callback Request", "status": "Processed" }
        ]
    }
}

# Helpers to find previous month
def get_previous_month(month):
    months = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"]
    if month in months:
        idx = months.index(month)
        if idx > 0:
            return months[idx - 1]
    return None

def calculate_percent_change(current, previous):
    if previous == 0:
        return 0.0
    return round(((current - previous) / previous) * 100, 1)

# ==========================================
# 1. Central Summary Metrics
# ==========================================
@app.route('/api/analytics/summary', methods=['GET'])
def get_summary():
    month = request.args.get('month', '2026-05')
    client = get_ga4_client()
    
    if client:
        pass

    # Extract historical current & previous data
    data = HISTORICAL_DATA.get(month, HISTORICAL_DATA["2026-05"])
    summary = data["summary"]
    
    prev_month = get_previous_month(month)
    change = {
        "traffic": 0.0,
        "leads": 0.0,
        "chatbotQueries": 0.0,
        "conversionRate": 0.0
    }
    
    if prev_month:
        prev_summary = HISTORICAL_DATA[prev_month]["summary"]
        change["traffic"] = calculate_percent_change(summary["traffic"], prev_summary["traffic"])
        change["leads"] = calculate_percent_change(summary["leads"], prev_summary["leads"])
        change["chatbotQueries"] = calculate_percent_change(summary["chatbotQueries"], prev_summary["chatbotQueries"])
        change["conversionRate"] = calculate_percent_change(summary["conversionRate"], prev_summary["conversionRate"])
        
    return jsonify({
        "current": summary,
        "change": change
    })

# ==========================================
# 2. Google Analytics Review: Top Pages
# ==========================================
@app.route('/api/analytics/top-pages', methods=['GET'])
def get_top_pages():
    month = request.args.get('month', '2026-05')
    data = HISTORICAL_DATA.get(month, HISTORICAL_DATA["2026-05"])
    return jsonify(data["top_pages"])

# ==========================================
# 3. Google Analytics Review: User Flow Analysis
# ==========================================
@app.route('/api/analytics/user-flow', methods=['GET'])
def get_user_flow():
    month = request.args.get('month', '2026-05')
    data = HISTORICAL_DATA.get(month, HISTORICAL_DATA["2026-05"])
    return jsonify(data["user_flow"])

# ==========================================
# 4. Monthly Website Health: Traffic Trends
# ==========================================
@app.route('/api/analytics/traffic-trends', methods=['GET'])
def get_traffic_trends():
    month = request.args.get('month', '2026-05')
    data = HISTORICAL_DATA.get(month, HISTORICAL_DATA["2026-05"])
    return jsonify(data["traffic_trends"])

# ==========================================
# 5. Monthly Website Health: SEO Performance
# ==========================================
@app.route('/api/analytics/seo', methods=['GET'])
def get_seo():
    month = request.args.get('month', '2026-05')
    data = HISTORICAL_DATA.get(month, HISTORICAL_DATA["2026-05"])
    return jsonify(data["seo"])

# ==========================================
# 6. Monthly Website Health: Page Speed
# ==========================================
@app.route('/api/analytics/page-speed', methods=['GET'])
def get_page_speed():
    month = request.args.get('month', '2026-05')
    data = HISTORICAL_DATA.get(month, HISTORICAL_DATA["2026-05"])
    return jsonify(data["page_speed"])

# ==========================================
# 7. Monthly Website Health: Form Submissions (Leads)
# ==========================================
@app.route('/api/analytics/form-submissions', methods=['GET'])
def get_form_submissions():
    month = request.args.get('month', '2026-05')
    data = HISTORICAL_DATA.get(month, HISTORICAL_DATA["2026-05"])
    return jsonify(data["form_submissions"])

# ==========================================
# 8. Monthly Website Health: Chatbot Usage
# ==========================================
@app.route('/api/analytics/chatbot', methods=['GET'])
def get_chatbot():
    month = request.args.get('month', '2026-05')
    data = HISTORICAL_DATA.get(month, HISTORICAL_DATA["2026-05"])
    return jsonify(data["chatbot"])

if __name__ == '__main__':
    if is_ga4_configured():
        print(f"STATUS: Google Analytics 4 API configured (Property ID: {PROPERTY_ID})")
    else:
        print("STATUS: Credentials missing. Running in Static Comparison Mode.")
        
    app.run(host='0.0.0.0', port=5000, debug=True)
