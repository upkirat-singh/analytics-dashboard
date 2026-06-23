import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TopPagesWidgetComponent } from './top-pages-widget';

describe('TopPagesWidget', () => {
  let component: TopPagesWidgetComponent;
  let fixture: ComponentFixture<TopPagesWidgetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TopPagesWidgetComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(TopPagesWidgetComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
