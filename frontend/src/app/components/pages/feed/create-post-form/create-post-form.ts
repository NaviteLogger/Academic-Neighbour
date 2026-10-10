import { CommonModule } from '@angular/common';
import { Component, computed, inject, output, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { PostCreate } from '../../../../models/post.model';

@Component({
    selector: 'app-create-post-form',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatCardModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
    ],
    templateUrl: './create-post-form.html',
    styleUrl: './create-post-form.css',
})
export class CreatePostFormComponent {
    private fb = inject(NonNullableFormBuilder);

    // Modern output() API
    createPost = output<PostCreate>();

    // Signal-based state
    readonly isExpanded = signal(false);

    readonly postForm = this.fb.group({
        content: ['', [Validators.required, Validators.maxLength(5000)]],
    });

    private readonly formValue = toSignal(this.postForm.valueChanges, { initialValue: this.postForm.value });

    readonly characterCount = computed(() => {
        const content = this.formValue()?.content || '';
        return content.length;
    });

    readonly characterCountColor = computed(() => {
        const count = this.characterCount();
        if (count > 4500) return 'text-red-500';
        if (count > 4000) return 'text-orange-500';
        return 'text-gray-500';
    });

    onFocus(): void {
        this.isExpanded.set(true);
    }

    onCancel(): void {
        this.isExpanded.set(false);
        this.postForm.reset();
    }

    onSubmit(): void {
        if (this.postForm.valid) {
            const postData: PostCreate = {
                content: this.postForm.value.content!.trim(),
            };
            this.createPost.emit(postData);
            this.postForm.reset();
            this.isExpanded.set(false);
        }
    }
}
