import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { GoogleAnalyticsService } from '../../../services/google-analytics.service';
import { WidgetConfigService } from '../../../services/widget-config.service';
import { switchMap } from 'rxjs';

@Component({
  selector: 'app-users-widget',
  imports: [CommonModule],
  templateUrl: './users-widget.html',
  styleUrl: './users-widget.css',
})
export class UsersWidgetComponent {
  private readonly gaService = inject(GoogleAnalyticsService);
  private readonly configService = inject(WidgetConfigService);

  // Automatically fetches summary metrics whenever the globally selected filter changes
  readonly metrics = toSignal(
    toObservable(this.configService.selectedFilter).pipe(
      switchMap(filter => this.gaService.getSummaryMetrics(filter.month, filter.country))
    )
  );
}
