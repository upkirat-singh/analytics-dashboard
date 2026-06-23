import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { GoogleAnalyticsService } from '../../../services/google-analytics.service';
import { WidgetConfigService } from '../../../services/widget-config.service';
import { switchMap } from 'rxjs';

@Component({
  selector: 'app-sessions-widget',
  imports: [CommonModule],
  templateUrl: './sessions-widget.html',
  styleUrl: './sessions-widget.css',
})
export class SessionsWidgetComponent {
  private readonly gaService = inject(GoogleAnalyticsService);
  private readonly configService = inject(WidgetConfigService);

  // Automatically fetches summary metrics whenever the globally selected month changes
  readonly metrics = toSignal(
    toObservable(this.configService.selectedMonth).pipe(
      switchMap(month => this.gaService.getSummaryMetrics(month))
    )
  );
}
