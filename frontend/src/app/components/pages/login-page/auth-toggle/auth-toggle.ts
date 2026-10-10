import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-auth-toggle',
  imports: [],
  templateUrl: './auth-toggle.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './auth-toggle.css',
})
export class AuthToggle {
  @Input({ required: true }) activeForm!: 'login' | 'register';
  @Output() formChange = new EventEmitter<'login' | 'register'>();
}
