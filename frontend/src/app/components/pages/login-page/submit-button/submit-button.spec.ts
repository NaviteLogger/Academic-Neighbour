import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SubmitButton } from './submit-button';

describe('SubmitButton', () => {
  let component: SubmitButton;
  let fixture: ComponentFixture<SubmitButton>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SubmitButton]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SubmitButton);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
