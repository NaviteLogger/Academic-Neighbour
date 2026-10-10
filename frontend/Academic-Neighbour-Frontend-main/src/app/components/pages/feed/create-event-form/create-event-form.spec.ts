import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatNativeDateModule } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CreateEventFormComponent } from './create-event-form';

describe('CreateEventFormComponent', () => {
    let component: CreateEventFormComponent;
    let fixture: ComponentFixture<CreateEventFormComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                CreateEventFormComponent,
                ReactiveFormsModule,
                MatFormFieldModule,
                MatInputModule,
                MatButtonModule,
                MatCardModule,
                MatDatepickerModule,
                MatNativeDateModule,
                BrowserAnimationsModule,
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(CreateEventFormComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should expand form on focus', () => {
        expect(component.isExpanded()).toBe(false);
        component.onFocus();
        expect(component.isExpanded()).toBe(true);
    });

    it('should emit createEvent when form is valid', () => {
        spyOn(component.createEvent, 'emit');

        const startDate = new Date();
        const endDate = new Date();
        endDate.setDate(endDate.getDate() + 1);

        component.eventForm.patchValue({
            title: 'Test Event',
            description: 'Test description for event',
            location: 'Test Location',
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
        });

        component.onSubmit();
        expect(component.createEvent.emit).toHaveBeenCalled();
    });

    it('should not emit createEvent when form is invalid', () => {
        spyOn(component.createEvent, 'emit');
        component.eventForm.patchValue({
            title: '',
            description: '',
            location: '',
            start_date: '',
            end_date: '',
        });

        component.onSubmit();
        expect(component.createEvent.emit).not.toHaveBeenCalled();
    });

    it('should reset form on cancel', () => {
        component.isExpanded.set(true);
        component.eventForm.patchValue({
            title: 'Test',
            description: 'Test description',
            location: 'Test location',
        });

        component.onCancel();
        expect(component.isExpanded()).toBe(false);
        expect(component.eventForm.value.title).toBe('');
    });
});
