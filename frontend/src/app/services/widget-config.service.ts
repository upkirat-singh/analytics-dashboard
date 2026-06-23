import { Injectable, signal } from '@angular/core';
import { Widget } from '../models/widget.model';

@Injectable({
  providedIn: 'root'
})
export class WidgetConfigService {
  private readonly STORAGE_KEY = 'dashboard_active_widgets';

  readonly availableWidgets: Widget[] = [
    { id: 'users', title: 'Users KPI', type: 'kpi' },
    { id: 'sessions', title: 'Sessions KPI', type: 'kpi' },
    { id: 'conversions', title: 'Conversions KPI', type: 'kpi' },
    { id: 'engagement', title: 'Engagement KPI', type: 'kpi' },
    { id: 'trafficTrends', title: 'Traffic Trends', type: 'chart' },
    { id: 'bounceRates', title: 'Bounce Rates & Pages', type: 'table' },
    { id: 'userFlow', title: 'User Flow Analysis', type: 'flow' },
    { id: 'seoPerformance', title: 'SEO Performance', type: 'health' },
    { id: 'pageSpeed', title: 'Page Speed Health', type: 'health' },
    { id: 'formSubmissions', title: 'Form Submissions (Leads)', type: 'table' },
    { id: 'chatbotUsage', title: 'Chatbot Metrics', type: 'chart' }
  ];

  // Signal for active widgets
  private activeWidgetsSignal = signal<string[]>(this.loadSavedWidgets());

  // Signal for globally selected month
  private selectedMonthSignal = signal<string>('2026-05');

  // Expose read-only signals
  readonly activeWidgets = this.activeWidgetsSignal.asReadonly();
  readonly selectedMonth = this.selectedMonthSignal.asReadonly();

  changeMonth(month: string): void {
    this.selectedMonthSignal.set(month);
  }

  // Computed helper to check if a widget is active
  isWidgetActive(id: string): boolean {
    return this.activeWidgetsSignal().includes(id);
  }

  toggleWidget(id: string): void {
    const current = this.activeWidgetsSignal();
    let updated: string[];
    if (current.includes(id)) {
      updated = current.filter(item => item !== id);
    } else {
      updated = [...current, id];
    }
    this.activeWidgetsSignal.set(updated);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(updated));
  }

  private loadSavedWidgets(): string[] {
    const saved = localStorage.getItem(this.STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Error loading saved widget configuration', e);
      }
    }
    // Default: all widgets active initially
    return this.availableWidgets.map(w => w.id);
  }
}
