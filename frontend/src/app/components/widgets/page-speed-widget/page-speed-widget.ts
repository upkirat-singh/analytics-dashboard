import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { GoogleAnalyticsService } from '../../../services/google-analytics.service';
import { WidgetConfigService } from '../../../services/widget-config.service';
import { switchMap } from 'rxjs';

@Component({
  selector: 'app-page-speed-widget',
  imports: [CommonModule],
  templateUrl: './page-speed-widget.html',
  styleUrl: './page-speed-widget.css',
})
export class PageSpeedWidgetComponent {
  private readonly gaService = inject(GoogleAnalyticsService);
  private readonly configService = inject(WidgetConfigService);

  // Automatically fetches page speed metrics whenever the globally selected month changes
  readonly speed = toSignal(
    toObservable(this.configService.selectedMonth).pipe(
      switchMap(month => this.gaService.getPageSpeed(month))
    )
  );
}
