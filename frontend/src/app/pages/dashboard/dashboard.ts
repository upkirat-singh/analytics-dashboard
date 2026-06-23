import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { UsersWidgetComponent } from '../../components/widgets/users-widget/users-widget';
import { SessionsWidgetComponent } from '../../components/widgets/sessions-widget/sessions-widget';
import { ConversionsWidgetComponent } from '../../components/widgets/conversions-widget/conversions-widget';
import { EngagementWidgetComponent } from '../../components/widgets/engagement-widget/engagement-widget';
import { TopPagesWidgetComponent } from '../../components/widgets/top-pages-widget/top-pages-widget';
import { TrafficSourcesWidgetComponent } from '../../components/widgets/traffic-sources-widget/traffic-sources-widget';
import { SeoPerformanceWidgetComponent } from '../../components/widgets/seo-performance-widget/seo-performance-widget';
import { PageSpeedWidgetComponent } from '../../components/widgets/page-speed-widget/page-speed-widget';
import { UserFlowWidgetComponent } from '../../components/widgets/user-flow-widget/user-flow-widget';
import { FormSubmissionsWidgetComponent } from '../../components/widgets/form-submissions-widget/form-submissions-widget';
import { ChatbotUsageWidgetComponent } from '../../components/widgets/chatbot-usage-widget/chatbot-usage-widget';
import { WidgetConfigService } from '../../services/widget-config.service';

@Component({
  selector: 'app-dashboard',
  imports: [
    CommonModule,
    UsersWidgetComponent,
    SessionsWidgetComponent,
    ConversionsWidgetComponent,
    EngagementWidgetComponent,
    TopPagesWidgetComponent,
    TrafficSourcesWidgetComponent,
    SeoPerformanceWidgetComponent,
    PageSpeedWidgetComponent,
    UserFlowWidgetComponent,
    FormSubmissionsWidgetComponent,
    ChatbotUsageWidgetComponent
  ],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class DashboardComponent {
  // Inject the configuration service
  readonly configService = inject(WidgetConfigService);

  // Expose signals to the template
  readonly activeWidgets = this.configService.activeWidgets;
  readonly availableWidgets = this.configService.availableWidgets;

  // Drawer menu visibility state
  isSettingsOpen = signal(false);

  // Toggle settings panel
  toggleSettings(): void {
    this.isSettingsOpen.update(val => !val);
  }

  // Handle month selector dropdown changes
  onMonthChange(event: Event): void {
    const select = event.target as HTMLSelectElement;
    if (select) {
      this.configService.changeMonth(select.value);
    }
  }
}
