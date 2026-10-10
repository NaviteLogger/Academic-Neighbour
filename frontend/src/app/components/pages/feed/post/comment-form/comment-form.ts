import { CommonModule } from '@angular/common';
import { Component, inject, input, output } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { CommentRequest } from '../../../../../models/comment.model';

@Component({
    selector: 'app-comment-form',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
    ],
    templateUrl: './comment-form.html',
    styleUrl: './comment-form.css',
})
export class CommentFormComponent {
    private fb = inject(NonNullableFormBuilder);

    // Inputs
    postId = input.required<number>();
    isEdit = input<boolean>(false);
    initialContent = input<string>('');

    // Outputs
    submitComment = output<CommentRequest>();
    cancelEdit = output<void>();

    // Form
    commentForm = this.fb.group({
        content: ['', [Validators.required, Validators.minLength(1), Validators.maxLength(500)]],
    });

    constructor() {
        // Watch for initial content changes (for edit mode)
        const initialValue = this.initialContent();
        if (initialValue) {
            this.commentForm.patchValue({ content: initialValue });
        }
    }

    onSubmit(): void {
        if (this.commentForm.valid) {
            const comment: CommentRequest = {
                content: this.commentForm.value.content!.trim(),
            };
            this.submitComment.emit(comment);

            // Reset form if not in edit mode
            if (!this.isEdit()) {
                this.commentForm.reset();
            }
        }
    }

    onCancel(): void {
        this.cancelEdit.emit();
        this.commentForm.reset();
    }

    get isFormValid(): boolean {
        return this.commentForm.valid;
    }

    get contentControl() {
        return this.commentForm.controls.content;
    }
}
