import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-contact-button',
  imports: [RouterLink],
  templateUrl: './contact-button.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './contact-button.css',
})
export class ContactButton {}
