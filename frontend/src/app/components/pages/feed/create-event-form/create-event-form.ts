import { CommonModule } from '@angular/common';
import { Component, inject, output, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { EventCreate } from '../../../../models/event.model';

@Component({
    selector: 'app-create-event-form',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatDatepickerModule,
        MatNativeDateModule,
    ],
    templateUrl: './create-event-form.html',
    styleUrl: './create-event-form.css',
})
export class CreateEventFormComponent {
    private fb = inject(NonNullableFormBuilder);

    // Modern output() API
    createEvent = output<EventCreate>();

    // Signal-based state
    readonly isExpanded = signal(false);

    readonly eventForm = this.fb.group({
        title: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(200)]],
        description: ['', [Validators.required, Validators.minLength(10), Validators.maxLength(2000)]],
        location: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(300)]],
        start_date: ['', [Validators.required]],
        end_date: ['', [Validators.required]],
    });

    readonly minDate = new Date();

    onFocus(): void {
        this.isExpanded.set(true);
    }

    onCancel(): void {
        this.isExpanded.set(false);
        this.eventForm.reset();
    }

    onSubmit(): void {
        if (this.eventForm.valid) {
            const formValue = this.eventForm.value;

            // Format dates to ISO string
            const startDate = new Date(formValue.start_date!);
            const endDate = new Date(formValue.end_date!);

            const eventData: EventCreate = {
                title: formValue.title!.trim(),
                description: formValue.description!.trim(),
                location: formValue.location!.trim(),
                start_date: startDate.toISOString(),
                end_date: endDate.toISOString(),
            };

            this.createEvent.emit(eventData);
            this.eventForm.reset();
            this.isExpanded.set(false);
        }
    }

    get titleControl() {
        return this.eventForm.controls.title;
    }

    get descriptionControl() {
        return this.eventForm.controls.description;
    }

    get locationControl() {
        return this.eventForm.controls.location;
    }

    get startDateControl() {
        return this.eventForm.controls.start_date;
    }

    get endDateControl() {
        return this.eventForm.controls.end_date;
    }
}
