import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormGroup, ReactiveFormsModule } from '@angular/forms';
import { SubmitButton } from '../submit-button/submit-button';
import { ValidationErrors } from '../validation-errors/validation-errors';

@Component({
    selector: 'app-login-form',
    standalone: true,
    imports: [CommonModule, ReactiveFormsModule, SubmitButton, ValidationErrors],
    templateUrl: './login-form.html',
    styleUrl: './login-form.css'
})
export class LoginForm {
    @Input({ required: true }) loginForm!: FormGroup;
    @Input() apiError: string | null = null;
    @Output() submitLogin = new EventEmitter<void>();
    @Output() switchToRegister = new EventEmitter<void>();

    onSubmit(): void {
        this.submitLogin.emit();
    }

    onSwitchToRegister(): void {
        this.switchToRegister.emit();
    }
}
