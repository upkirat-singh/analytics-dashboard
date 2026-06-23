import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { GoogleAnalyticsService } from '../../../services/google-analytics.service';
import { WidgetConfigService } from '../../../services/widget-config.service';
import { switchMap } from 'rxjs';

@Component({
  selector: 'app-form-submissions-widget',
  imports: [CommonModule],
  templateUrl: './form-submissions-widget.html',
  styleUrl: './form-submissions-widget.css',
})
export class FormSubmissionsWidgetComponent {
  private readonly gaService = inject(GoogleAnalyticsService);
  private readonly configService = inject(WidgetConfigService);

  // Automatically fetches form submissions metrics whenever the globally selected month changes
  readonly leads = toSignal(
    toObservable(this.configService.selectedMonth).pipe(
      switchMap(month => this.gaService.getFormSubmissions(month))
    )
  );
}
