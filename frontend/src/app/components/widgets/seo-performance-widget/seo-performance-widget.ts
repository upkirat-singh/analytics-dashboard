import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { GoogleAnalyticsService } from '../../../services/google-analytics.service';
import { WidgetConfigService } from '../../../services/widget-config.service';
import { switchMap } from 'rxjs';

@Component({
  selector: 'app-seo-performance-widget',
  imports: [CommonModule],
  templateUrl: './seo-performance-widget.html',
  styleUrl: './seo-performance-widget.css',
})
export class SeoPerformanceWidgetComponent {
  private readonly gaService = inject(GoogleAnalyticsService);
  private readonly configService = inject(WidgetConfigService);

  // Automatically fetches SEO details whenever the globally selected month changes
  readonly seo = toSignal(
    toObservable(this.configService.selectedMonth).pipe(
      switchMap(month => this.gaService.getSEOPerformance(month))
    )
  );
}
