import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormControl, Validators } from '@angular/forms';

import { ValidationErrors } from './validation-errors';

describe('ValidationErrors', () => {
  let component: ValidationErrors;
  let fixture: ComponentFixture<ValidationErrors>;
  let control: FormControl<string | null>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ValidationErrors],
    }).compileComponents();

    control = new FormControl('', Validators.required);
    fixture = TestBed.createComponent(ValidationErrors);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('control', control);
    fixture.componentRef.setInput('controlName', 'Hasło');
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should show errors when the same control becomes touched', () => {
    const element = fixture.nativeElement as HTMLElement;
    expect(element.textContent).not.toContain('jest polem wymaganym');

    control.markAsTouched();
    fixture.detectChanges();

    expect(element.textContent).toContain('Hasło jest polem wymaganym.');
  });
});
