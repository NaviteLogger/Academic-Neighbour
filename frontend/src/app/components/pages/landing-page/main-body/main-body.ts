import { Component, ChangeDetectionStrategy } from '@angular/core';
import { LoginButton } from '../buttons/login-button/login-button';

@Component({
  selector: 'app-main-body',
  imports: [LoginButton],
  templateUrl: './main-body.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './main-body.css',
})
export class MainBody {}
