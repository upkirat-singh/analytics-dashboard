import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { GoogleAnalyticsService } from '../../../services/google-analytics.service';
import { WidgetConfigService } from '../../../services/widget-config.service';
import { switchMap } from 'rxjs';

@Component({
  selector: 'app-traffic-sources-widget',
  imports: [CommonModule],
  templateUrl: './traffic-sources-widget.html',
  styleUrl: './traffic-sources-widget.css',
})
export class TrafficSourcesWidgetComponent {
  private readonly gaService = inject(GoogleAnalyticsService);
  private readonly configService = inject(WidgetConfigService);

  // Automatically fetches traffic trends metrics whenever the globally selected month changes
  readonly trends = toSignal(
    toObservable(this.configService.selectedMonth).pipe(
      switchMap(month => this.gaService.getTrafficTrends(month))
    )
  );
}
