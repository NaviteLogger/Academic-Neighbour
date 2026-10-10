import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-about-us-button',
  imports: [RouterLink],
  templateUrl: './about-us-button.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './about-us-button.css',
})
export class AboutUsButton {}
