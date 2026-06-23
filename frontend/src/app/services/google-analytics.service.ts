import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
  score: number;
  keywords: SEOKeyword[];
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
}

@Injectable({
  providedIn: 'root'
})
export class GoogleAnalyticsService {
  private readonly http = inject(HttpClient);
  private readonly API_URL = 'http://localhost:5000/api/analytics';

  // 1. Google Analytics Review Data
  getTopPages(month: string = '2026-05'): Observable<PageMetric[]> {
    return this.http.get<PageMetric[]>(`${this.API_URL}/top-pages?month=${month}`);
  }

  getUserFlow(month: string = '2026-05'): Observable<UserFlowStage[]> {
    return this.http.get<UserFlowStage[]>(`${this.API_URL}/user-flow?month=${month}`);
  }

  // 2. Monthly Website Health Data
  getTrafficTrends(month: string = '2026-05'): Observable<TrafficTrend[]> {
    return this.http.get<TrafficTrend[]>(`${this.API_URL}/traffic-trends?month=${month}`);
  }

  getSEOPerformance(month: string = '2026-05'): Observable<SEOPerformance> {
    return this.http.get<SEOPerformance>(`${this.API_URL}/seo?month=${month}`);
  }

  getPageSpeed(month: string = '2026-05'): Observable<PageSpeedMetrics> {
    return this.http.get<PageSpeedMetrics>(`${this.API_URL}/page-speed?month=${month}`);
  }

  getFormSubmissions(month: string = '2026-05'): Observable<LeadLog[]> {
    return this.http.get<LeadLog[]>(`${this.API_URL}/form-submissions?month=${month}`);
  }

  getChatbotUsage(month: string = '2026-05'): Observable<ChatbotUsageMetrics> {
    return this.http.get<ChatbotUsageMetrics>(`${this.API_URL}/chatbot?month=${month}`);
  }

  // 3. Centralized Dashboard Summary Metrics
  getSummaryMetrics(month: string = '2026-05'): Observable<SummaryMetrics> {
    return this.http.get<SummaryMetrics>(`${this.API_URL}/summary?month=${month}`);
  }
}
