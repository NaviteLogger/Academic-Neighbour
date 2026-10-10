import { Component } from '@angular/core';
import { Footer } from "../landing-page/footer/footer";
import { Header } from "../landing-page/header/header";

@Component({
  selector: 'app-about-us-page',
  imports: [Header, Footer],
  templateUrl: './about-us-page.html',
  styleUrl: './about-us-page.css',
})
export class AboutUsPage {

}
