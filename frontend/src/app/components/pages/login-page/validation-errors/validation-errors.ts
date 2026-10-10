import { ChangeDetectorRef, Component, effect, inject, input } from '@angular/core';

import { AbstractControl } from '@angular/forms';

@Component({
  selector: 'app-validation-errors',
  imports: [],
  templateUrl: './validation-errors.html',
  styleUrl: './validation-errors.css',
})
export class ValidationErrors {
  private readonly cdr = inject(ChangeDetectorRef);

  readonly control = input.required<AbstractControl | null>();
  readonly controlName = input('To pole');

  constructor() {
    // The control instance stays the same while its state changes, so re-render on its events.
    effect((onCleanup) => {
      const subscription = this.control()?.events.subscribe(() => this.cdr.markForCheck());
      onCleanup(() => subscription?.unsubscribe());
    });
  }
}
