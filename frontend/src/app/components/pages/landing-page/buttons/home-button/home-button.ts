import { Component, ChangeDetectionStrategy } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-home-button',
  imports: [RouterLink],
  templateUrl: './home-button.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './home-button.css',
})
export class HomeButton {}
