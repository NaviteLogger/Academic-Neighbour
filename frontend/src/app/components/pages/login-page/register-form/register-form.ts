import { Component, EventEmitter, Input, Output, ChangeDetectionStrategy } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { SubmitButton } from '../submit-button/submit-button';
import { ValidationErrors } from '../validation-errors/validation-errors';

@Component({
  selector: 'app-register-form',
  standalone: true,
  imports: [ReactiveFormsModule, SubmitButton, ValidationErrors],
  templateUrl: './register-form.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './register-form.css',
})
export class RegisterForm {
  @Input({ required: true }) registerForm!: FormGroup;
  @Input() apiError: string | null = null;
  @Output() submitRegister = new EventEmitter<void>();
  @Output() switchToLogin = new EventEmitter<void>();

  onSubmit(): void {
    this.submitRegister.emit();
  }

  onSwitchToLogin(): void {
    this.switchToLogin.emit();
  }
}
