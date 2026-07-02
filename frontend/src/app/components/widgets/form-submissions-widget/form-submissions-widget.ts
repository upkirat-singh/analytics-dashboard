import { Component, inject, OnDestroy } from '@angular/core';
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
export class FormSubmissionsWidgetComponent implements OnDestroy {
  private readonly gaService = inject(GoogleAnalyticsService);
  private readonly configService = inject(WidgetConfigService);
  private backdropEl: HTMLElement | null = null;

  isExpanded = false;

  toggleExpand() {
    this.isExpanded = !this.isExpanded;
    if (this.isExpanded) {
      this.backdropEl = document.createElement('div');
      this.backdropEl.className = 'widget-backdrop';
      this.backdropEl.addEventListener('click', () => this.toggleExpand());
      document.body.appendChild(this.backdropEl);
    } else {
      this.backdropEl?.remove();
      this.backdropEl = null;
    }
  }

  ngOnDestroy() { this.backdropEl?.remove(); }

  readonly leads = toSignal(
    toObservable(this.configService.selectedFilter).pipe(
      switchMap(filter => this.gaService.getFormSubmissions(filter.month, filter.country))
    )
  );
}
