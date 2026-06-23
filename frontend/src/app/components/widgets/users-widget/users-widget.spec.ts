import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UsersWidgetComponent } from './users-widget';

describe('UsersWidget', () => {
  let component: UsersWidgetComponent;
  let fixture: ComponentFixture<UsersWidgetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UsersWidgetComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(UsersWidgetComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
