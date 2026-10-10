import { CommonModule } from '@angular/common';
import { Component, computed, inject, input, output, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router } from '@angular/router';
import { CommentRequest, CommentWithAuthor } from '../../../../../models/comment.model';
import { AuthService } from '../../../../../services/auth.service';
import { CommentFormComponent } from '../comment-form/comment-form';

@Component({
    selector: 'app-comment-list',
    standalone: true,
    imports: [
        CommonModule,
        MatButtonModule,
        MatIconModule,
        MatTooltipModule,
        CommentFormComponent,
    ],
    templateUrl: './comment-list.html',
    styleUrl: './comment-list.css',
})
export class CommentListComponent {
    private authService = inject(AuthService);
    private router = inject(Router);

    // Inputs
    comments = input.required<CommentWithAuthor[]>();
    postId = input.required<number>();

    // Outputs
    deleteComment = output<number>();
    updateComment = output<{ commentId: number; content: CommentRequest }>();

    // State
    editingCommentId = signal<number | null>(null);

    // Computed
    readonly sortedComments = computed(() => {
        return [...this.comments()].sort((a, b) => {
            return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
        });
    });

    readonly currentUserId = computed(() => this.authService.currentUser()?.id);

    canEditComment(comment: CommentWithAuthor): boolean {
        const userId = this.currentUserId();
        const userRole = this.authService.currentUser()?.role;
        return comment.author_id === userId || userRole === 'admin';
    }

    canDeleteComment(comment: CommentWithAuthor): boolean {
        const userId = this.currentUserId();
        const userRole = this.authService.currentUser()?.role;
        return comment.author_id === userId || userRole === 'admin';
    }

    startEdit(commentId: number): void {
        this.editingCommentId.set(commentId);
    }

    cancelEdit(): void {
        this.editingCommentId.set(null);
    }

    onUpdateComment(commentId: number, content: CommentRequest): void {
        this.updateComment.emit({ commentId, content });
        this.editingCommentId.set(null);
    }

    onDeleteComment(commentId: number): void {
        if (confirm('Czy na pewno chcesz usunąć ten komentarz?')) {
            this.deleteComment.emit(commentId);
        }
    }

    getFormattedDate(dateString: string): string {
        const now = new Date();
        const commentDate = new Date(dateString);
        const diffInMs = now.getTime() - commentDate.getTime();
        const diffInMinutes = Math.floor(diffInMs / 60000);
        const diffInHours = Math.floor(diffInMs / 3600000);
        const diffInDays = Math.floor(diffInMs / 86400000);

        if (diffInMinutes < 1) {
            return 'teraz';
        } else if (diffInMinutes < 60) {
            return `${diffInMinutes} min temu`;
        } else if (diffInHours < 24) {
            return `${diffInHours} godz. temu`;
        } else if (diffInDays < 7) {
            return `${diffInDays} dni temu`;
        } else {
            return commentDate.toLocaleDateString('pl-PL');
        }
    }

    getAuthorInitial(authorId: number): string {
        return `U${authorId}`;
    }

    navigateToProfile(authorId: number): void {
        this.router.navigate(['/profile', authorId]);
    }
}
