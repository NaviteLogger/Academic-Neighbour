import { Component } from '@angular/core';
import { RouterLink } from "@angular/router";
import { AboutUsButton } from '../buttons/about-us-button/about-us-button';
import { ContactButton } from '../buttons/contact-button/contact-button';
import { HomeButton } from '../buttons/home-button/home-button';
import { LoginButton } from '../buttons/login-button/login-button';

@Component({
  selector: 'app-header',
  imports: [LoginButton, HomeButton, ContactButton, AboutUsButton, RouterLink],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {

}
