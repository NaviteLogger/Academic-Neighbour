import { CommonModule } from '@angular/common';
import { Component, computed, inject, input, output, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router } from '@angular/router';
import { CommentRequest, CommentWithAuthor } from '../../../../models/comment.model';
import { Post } from '../../../../models/post.model';
import { CommentService } from '../../../../services/comment.service';
import { CommentFormComponent } from './comment-form/comment-form';
import { CommentListComponent } from './comment-list/comment-list';

@Component({
    selector: 'app-post',
    standalone: true,
    imports: [
        CommonModule,
        MatCardModule,
        MatButtonModule,
        MatIconModule,
        MatTooltipModule,
        MatProgressSpinnerModule,
        CommentFormComponent,
        CommentListComponent,
    ],
    templateUrl: './post.html',
    styleUrl: './post.css',
})
export class PostComponent {
    private commentService = inject(CommentService);
    private router = inject(Router);

    // Modern input() API
    post = input.required<Post>();

    // Modern output() API
    likePost = output<number>();
    refreshPost = output<void>();

    // State
    readonly showComments = signal(false);
    readonly comments = signal<CommentWithAuthor[]>([]);
    readonly isLoadingComments = signal(false);
    readonly commentError = signal<string | null>(null);

    // Computed signals
    readonly formattedDate = computed(() => this.getFormattedDate(this.post().created_at || ''));
    readonly authorInitial = computed(() => {
        const post = this.post();
        if (post.author_first_name && post.author_last_name) {
            return `${post.author_first_name[0]}${post.author_last_name[0]}`.toUpperCase();
        }
        if (post.author_username) {
            return post.author_username.substring(0, 2).toUpperCase();
        }
        return 'U';
    });
    readonly authorName = computed(() => {
        const post = this.post();
        if (post.author_first_name && post.author_last_name) {
            return `${post.author_first_name} ${post.author_last_name}`;
        }
        if (post.author_username) {
            return post.author_username;
        }
        return `Użytkownik #${post.author_id}`;
    });

    onLike(): void {
        const postId = this.post().id;
        if (postId) {
            this.likePost.emit(postId);
        }
    }

    onNavigateToProfile(): void {
        const authorId = this.post().author_id;
        if (authorId) {
            this.router.navigate(['/profile', authorId]);
        }
    }

    onToggleComments(): void {
        const isCurrentlyShowing = this.showComments();
        this.showComments.set(!isCurrentlyShowing);

        // Load comments when opening for the first time
        if (!isCurrentlyShowing && this.comments().length === 0) {
            this.loadComments();
        }
    }

    loadComments(): void {
        const postId = this.post().id;
        if (!postId) return;

        this.isLoadingComments.set(true);
        this.commentError.set(null);

        this.commentService.getPostComments(postId).subscribe({
            next: (comments) => {
                this.comments.set(comments);
                this.isLoadingComments.set(false);
            },
            error: (error) => {
                console.error('Failed to load comments:', error);
                this.commentError.set('Nie udało się załadować komentarzy.');
                this.isLoadingComments.set(false);
            },
        });
    }

    onCreateComment(comment: CommentRequest): void {
        const postId = this.post().id;
        if (!postId) return;

        this.commentService.createComment(postId, comment).subscribe({
            next: (newComment) => {
                this.comments.update(current => [newComment, ...current]);
                this.refreshPost.emit(); // Refresh to update comment count
            },
            error: (error) => {
                console.error('Failed to create comment:', error);
                this.commentError.set('Nie udało się dodać komentarza.');
            },
        });
    }

    onUpdateComment(data: { commentId: number; content: CommentRequest }): void {
        this.commentService.updateComment(data.commentId, data.content).subscribe({
            next: (updatedComment) => {
                this.comments.update(current =>
                    current.map(c => (c.id === data.commentId ? updatedComment : c))
                );
            },
            error: (error) => {
                console.error('Failed to update comment:', error);
                this.commentError.set('Nie udało się zaktualizować komentarza.');
            },
        });
    }

    onDeleteComment(commentId: number): void {
        this.commentService.deleteComment(commentId).subscribe({
            next: () => {
                this.comments.update(current => current.filter(c => c.id !== commentId));
                this.refreshPost.emit(); // Refresh to update comment count
            },
            error: (error) => {
                console.error('Failed to delete comment:', error);
                this.commentError.set('Nie udało się usunąć komentarza.');
            },
        });
    }

    private getFormattedDate(dateString: string): string {
        const now = new Date();
        const postDate = new Date(dateString);
        const diffInMs = now.getTime() - postDate.getTime();
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
            return postDate.toLocaleDateString('pl-PL');
        }
    }
}
