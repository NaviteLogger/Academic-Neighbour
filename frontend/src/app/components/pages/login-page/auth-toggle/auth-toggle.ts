import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-auth-toggle',
  imports: [],
  templateUrl: './auth-toggle.html',
  styleUrl: './auth-toggle.css',
})
export class AuthToggle {
  @Input({ required: true }) activeForm!: 'login' | 'register';
  @Output() formChange = new EventEmitter<'login' | 'register'>();
}
