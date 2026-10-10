import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';

@Component({
  selector: 'app-submit-button',
  imports: [],
  templateUrl: './submit-button.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './submit-button.css',
})
export class SubmitButton {
  @Input() text = 'Submit';
  @Input() disabled = false;
  @Output() buttonClick = new EventEmitter<void>();
}
