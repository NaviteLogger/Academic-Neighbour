import { Component } from '@angular/core';
import { Footer } from "../landing-page/footer/footer";
import { Header } from "../landing-page/header/header";

@Component({
  selector: 'app-contact-page',
  imports: [Header, Footer],
  templateUrl: './contact-page.html',
  styleUrl: './contact-page.css',
})
export class ContactPage {

}
