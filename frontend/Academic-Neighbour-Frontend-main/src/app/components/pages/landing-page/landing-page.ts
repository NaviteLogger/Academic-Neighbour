import { Component } from '@angular/core';
import { Header } from "./header/header";
import { MainBody } from './main-body/main-body';
import { Footer } from './footer/footer';

@Component({
  selector: 'app-landing-page',
  imports: [Header, MainBody, Footer],
  templateUrl: './landing-page.html',
  styleUrl: './landing-page.css',
})
export class LandingPage {

}
