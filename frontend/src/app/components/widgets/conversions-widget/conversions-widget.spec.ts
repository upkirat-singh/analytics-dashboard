import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConversionsWidgetComponent } from './conversions-widget';

describe('ConversionsWidget', () => {
  let component: ConversionsWidgetComponent;
  let fixture: ComponentFixture<ConversionsWidgetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConversionsWidgetComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(ConversionsWidgetComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
