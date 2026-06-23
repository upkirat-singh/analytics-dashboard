import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TrafficSourcesWidgetComponent } from './traffic-sources-widget';

describe('TrafficSourcesWidget', () => {
  let component: TrafficSourcesWidgetComponent;
  let fixture: ComponentFixture<TrafficSourcesWidgetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TrafficSourcesWidgetComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TrafficSourcesWidgetComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
