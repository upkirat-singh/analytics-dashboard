import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, catchError } from 'rxjs';

export interface PageMetric {
  url: string;
  views: number;
  bounceRate: number;
}

export interface SEOKeyword {
  keyword: string;
  position: number;
  searches: number;
}

export interface SEOPerformance {
  score: number | null;
  keywords: SEOKeyword[];
  note?: string;
}

export interface PageSpeedMetrics {
  score: number;
  lcp: number;
  fid: number;
  cls: number;
}

export interface LeadLog {
  timestamp: string;
  source: string;
  status: string;
}

export interface ChatbotUsageMetrics {
  chatsInitiated: number;
  resolutionRate: number;
  avgResponseTime: number;
}

export interface UserFlowStage {
  stage: string;
  page: string;
  dropoffRate: number;
  visitors: number;
}

export interface TrafficTrend {
  date: string;
  views: number;
  organic: number;
  direct: number;
  referral: number;
}

export interface SummaryMetricValues {
  traffic: number;
  leads: number;
  chatbotQueries: number;
  conversionRate: number;
}

export interface SummaryMetrics {
  current: SummaryMetricValues;
  change: SummaryMetricValues;
  source?: string;
}

@Injectable({
  providedIn: 'root'
})
export class GoogleAnalyticsService {
  private readonly http = inject(HttpClient);
  private readonly API_URL = 'http://localhost:5000/api/analytics';

  // Holds whether the active country credentials configuration is missing or invalid
  readonly isCredentialsError = signal(false);

  // 1. Google Analytics Review Data
  getTopPages(month: string = '2026-05', country: string = 'in'): Observable<PageMetric[]> {
    return this.http.get<PageMetric[]>(`${this.API_URL}/top-pages?month=${month}&country=${country}`);
  }

  getUserFlow(month: string = '2026-05', country: string = 'in'): Observable<UserFlowStage[]> {
    return this.http.get<UserFlowStage[]>(`${this.API_URL}/user-flow?month=${month}&country=${country}`);
  }

  // 2. Monthly Website Health Data
  getTrafficTrends(month: string = '2026-05', country: string = 'in'): Observable<TrafficTrend[]> {
    return this.http.get<TrafficTrend[]>(`${this.API_URL}/traffic-trends?month=${month}&country=${country}`);
  }

  getSEOPerformance(month: string = '2026-05', country: string = 'in'): Observable<SEOPerformance> {
    return this.http.get<SEOPerformance>(`${this.API_URL}/seo?month=${month}&country=${country}`);
  }

  getPageSpeed(month: string = '2026-05', country: string = 'in'): Observable<PageSpeedMetrics> {
    return this.http.get<PageSpeedMetrics>(`${this.API_URL}/page-speed?month=${month}&country=${country}`);
  }

  getFormSubmissions(month: string = '2026-05', country: string = 'in'): Observable<LeadLog[]> {
    return this.http.get<LeadLog[]>(`${this.API_URL}/form-submissions?month=${month}&country=${country}`);
  }

  getChatbotUsage(month: string = '2026-05', country: string = 'in'): Observable<ChatbotUsageMetrics> {
    return this.http.get<ChatbotUsageMetrics>(`${this.API_URL}/chatbot?month=${month}&country=${country}`);
  }

  // 3. Centralized Dashboard Summary Metrics
  getSummaryMetrics(month: string = '2026-05', country: string = 'in'): Observable<SummaryMetrics> {
    return this.http.get<SummaryMetrics>(`${this.API_URL}/summary?month=${month}&country=${country}`).pipe(
      tap(res => {
        this.isCredentialsError.set(res.source === 'unavailable');
      }),
      catchError(err => {
        this.isCredentialsError.set(true);
        throw err;
      })
    );
  }
}
