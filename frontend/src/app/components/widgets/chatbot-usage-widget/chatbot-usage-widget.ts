import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { GoogleAnalyticsService } from '../../../services/google-analytics.service';
import { WidgetConfigService } from '../../../services/widget-config.service';
import { switchMap } from 'rxjs';

@Component({
  selector: 'app-chatbot-usage-widget',
  imports: [CommonModule],
  templateUrl: './chatbot-usage-widget.html',
  styleUrl: './chatbot-usage-widget.css',
})
export class ChatbotUsageWidgetComponent {
  private readonly gaService = inject(GoogleAnalyticsService);
  private readonly configService = inject(WidgetConfigService);

  // Automatically fetches chatbot metrics whenever the globally selected month changes
  readonly chatbot = toSignal(
    toObservable(this.configService.selectedMonth).pipe(
      switchMap(month => this.gaService.getChatbotUsage(month))
    )
  );
}
