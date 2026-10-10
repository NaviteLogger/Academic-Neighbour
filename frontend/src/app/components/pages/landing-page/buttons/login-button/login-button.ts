import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-login-button',
  imports: [RouterLink],
  templateUrl: './login-button.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './login-button.css',
})
export class LoginButton {}
