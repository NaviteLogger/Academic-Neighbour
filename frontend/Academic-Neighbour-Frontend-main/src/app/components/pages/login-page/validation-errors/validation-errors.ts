import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { AbstractControl } from '@angular/forms';

@Component({
  selector: 'app-validation-errors',
  imports: [CommonModule],
  templateUrl: './validation-errors.html',
  styleUrl: './validation-errors.css',
})
export class ValidationErrors {
  @Input({ required: true }) control: AbstractControl | null = null;
  @Input() controlName = 'To pole';
}
