import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { HomeButton } from './home-button';

describe('HomeButton', () => {
  let component: HomeButton;
  let fixture: ComponentFixture<HomeButton>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HomeButton],
      providers: [provideRouter([])]
    })
      .compileComponents();

    fixture = TestBed.createComponent(HomeButton);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
