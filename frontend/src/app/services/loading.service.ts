import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class LoadingService {
  private activeRequests = 0;
  private isLoadingSignal = signal(false);

  readonly isLoading = this.isLoadingSignal.asReadonly();

  show(): void {
    this.activeRequests++;
    this.isLoadingSignal.set(true);
  }

  hide(): void {
    this.activeRequests = Math.max(0, this.activeRequests - 1);
    if (this.activeRequests === 0) {
      this.isLoadingSignal.set(false);
    }
  }
}
