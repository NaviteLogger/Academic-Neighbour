import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { ContactButton } from './contact-button';

describe('ContactButton', () => {
  let component: ContactButton;
  let fixture: ComponentFixture<ContactButton>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContactButton],
      providers: [provideRouter([])]
    })
      .compileComponents();

    fixture = TestBed.createComponent(ContactButton);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
