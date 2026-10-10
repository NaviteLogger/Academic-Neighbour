import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
@Component({
  selector: 'app-submit-button',
  imports: [CommonModule],
  templateUrl: './submit-button.html',
  styleUrl: './submit-button.css',
})
export class SubmitButton {
  @Input() text = 'Submit';
  @Input() disabled = false;
  @Output() buttonClick = new EventEmitter<void>();
}
