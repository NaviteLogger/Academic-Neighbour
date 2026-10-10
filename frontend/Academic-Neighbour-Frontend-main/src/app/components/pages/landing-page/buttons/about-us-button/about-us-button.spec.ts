import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { AboutUsButton } from './about-us-button';

describe('AboutUsButton', () => {
  let component: AboutUsButton;
  let fixture: ComponentFixture<AboutUsButton>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AboutUsButton],
      providers: [provideRouter([])]
    })
      .compileComponents();

    fixture = TestBed.createComponent(AboutUsButton);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
