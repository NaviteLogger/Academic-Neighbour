import { Component, Input, ChangeDetectionStrategy } from '@angular/core';

import { AbstractControl } from '@angular/forms';

@Component({
  selector: 'app-validation-errors',
  imports: [],
  templateUrl: './validation-errors.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './validation-errors.css',
})
export class ValidationErrors {
  @Input({ required: true }) control: AbstractControl | null = null;
  @Input() controlName = 'To pole';
}
