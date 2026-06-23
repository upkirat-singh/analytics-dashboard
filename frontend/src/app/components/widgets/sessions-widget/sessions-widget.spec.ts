import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SessionsWidgetComponent } from './sessions-widget';

describe('SessionsWidget', () => {
  let component: SessionsWidgetComponent;
  let fixture: ComponentFixture<SessionsWidgetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SessionsWidgetComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SessionsWidgetComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
