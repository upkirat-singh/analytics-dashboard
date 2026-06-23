import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EngagementWidgetComponent } from './engagement-widget';

describe('EngagementWidget', () => {
  let component: EngagementWidgetComponent;
  let fixture: ComponentFixture<EngagementWidgetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EngagementWidgetComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(EngagementWidgetComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
