import { CommonModule } from '@angular/common';
import { Component, effect, input, output } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

@Component({
    selector: 'app-profile-comment-form',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
    ],
    templateUrl: './profile-comment-form.html',
    styleUrl: './profile-comment-form.css',
})
export class ProfileCommentFormComponent {
    readonly submitComment = output<string>();
    readonly cancelForm = output<void>();
    readonly isSubmitting = input<boolean>(false);
    readonly errorMessage = input<string | null>(null);
    readonly resetForm = input<boolean>(false);

    readonly commentControl = new FormControl('', {
        validators: [Validators.required, Validators.minLength(1), Validators.maxLength(500)],
        nonNullable: true,
    });

    constructor() {
        // Reset form when resetForm input changes to true
        effect(() => {
            if (this.resetForm()) {
                this.commentControl.reset();
            }
        });
    }

    onSubmit(): void {
        if (this.commentControl.invalid || this.isSubmitting()) {
            this.commentControl.markAsTouched();
            return;
        }

        const content = this.commentControl.value.trim();
        if (!content) {
            return;
        }

        this.submitComment.emit(content);
        // Don't reset here - let the parent component handle success/error
    }

    onCancel(): void {
        this.commentControl.reset();
        this.cancelForm.emit();
    }

    getCharacterCount(): string {
        return `${this.commentControl.value.length}/500`;
    }
}
