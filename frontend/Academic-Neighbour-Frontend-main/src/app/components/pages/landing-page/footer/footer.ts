import { Component, signal } from '@angular/core';
import { AboutUsButton } from '../buttons/about-us-button/about-us-button';
import { ContactButton } from '../buttons/contact-button/contact-button';
import { HomeButton } from '../buttons/home-button/home-button';

@Component({
  selector: 'app-footer',
  imports: [HomeButton, AboutUsButton, ContactButton],
  templateUrl: './footer.html',
  styleUrl: './footer.css',
})
export class Footer {
  readonly currentYear = signal(new Date().getFullYear());
}
