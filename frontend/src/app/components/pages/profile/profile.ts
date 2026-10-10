import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, effect, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ActivatedRoute } from '@angular/router';
import { UserRead } from '../../../models/auth.model';
import { ProfileComment } from '../../../models/review.model';
import { AuthService } from '../../../services/auth.service';
import { ReviewService } from '../../../services/review.service';
import { UserService } from '../../../services/user.service';
import { FeedHeaderComponent } from '../feed/feed-header/feed-header';
import { ProfileCommentFormComponent } from './profile-comment-form/profile-comment-form';
import { ProfileCommentListComponent } from './profile-comment-list/profile-comment-list';

@Component({
    selector: 'app-profile',
    standalone: true,
    imports: [
        CommonModule,
        MatIconModule,
        MatButtonModule,
        MatCardModule,
        MatProgressSpinnerModule,
        MatTooltipModule,
        FeedHeaderComponent,
        ProfileCommentFormComponent,
        ProfileCommentListComponent,
    ],
    templateUrl: './profile.html',
    styleUrl: './profile.css',
})
export class ProfilePage implements OnInit {
    private authService = inject(AuthService);
    private userService = inject(UserService);
    private reviewService = inject(ReviewService);
    private route = inject(ActivatedRoute);

    readonly currentUser = this.authService.currentUser;
    readonly profileUser = signal<UserRead | null>(null);
    readonly profileUserId = signal<number | null>(null);
    readonly isLoading = signal(false);
    readonly isLoadingProfile = signal(false);
    readonly comments = signal<ProfileComment[]>([]);
    readonly showCommentForm = signal(false);
    readonly isLoadingComments = signal(false);
    readonly isSubmittingComment = signal(false);
    readonly commentError = signal<string | null>(null);
    readonly resetCommentForm = signal(false);

    readonly isOwnProfile = computed(() => {
        const current = this.currentUser();
        const profileId = this.profileUserId();
        return current && profileId && current.id === profileId;
    });

    readonly userInitials = computed(() => {
        const user = this.profileUser();
        if (!user) return 'U';

        const firstInitial = user.first_name?.[0]?.toUpperCase() || '';
        const lastInitial = user.last_name?.[0]?.toUpperCase() || '';
        return firstInitial + lastInitial || user.username?.[0]?.toUpperCase() || 'U';
    });

    readonly userFullName = computed(() => {
        const user = this.profileUser();
        if (!user) return 'Ładowanie...';
        return `${user.first_name} ${user.last_name}`.trim() || user.username || 'Użytkownik';
    });

    constructor() {
        // React to route param changes
        effect(() => {
            this.route.paramMap.subscribe(params => {
                const id = params.get('id');
                if (id) {
                    const userId = Number(id);
                    this.profileUserId.set(userId);
                    this.loadProfile(userId);
                    this.loadComments(userId);
                }
            });
        });
    }

    ngOnInit(): void {
        // Initial load
        const id = this.route.snapshot.paramMap.get('id');
        if (id) {
            const userId = Number(id);
            this.profileUserId.set(userId);
            this.loadProfile(userId);
            this.loadComments(userId);
        }
    }

    loadProfile(userId: number): void {
        this.isLoadingProfile.set(true);

        this.userService.getUserProfile(userId).subscribe({
            next: (user: UserRead) => {
                this.profileUser.set(user);
                this.isLoadingProfile.set(false);
            },
            error: (error: Error) => {
                console.error('Failed to load profile:', error);
                this.isLoadingProfile.set(false);
            },
        });
    }

    loadComments(userId: number): void {
        if (!userId) return;

        this.isLoadingComments.set(true);

        this.reviewService.getUserComments(userId).subscribe({
            next: (comments) => {
                this.comments.set(comments);
                this.isLoadingComments.set(false);
            },
            error: (error) => {
                console.error('Failed to load comments:', error);
                this.isLoadingComments.set(false);
            },
        });
    }

    toggleCommentForm(): void {
        // Prevent users from commenting on their own profile
        if (this.isOwnProfile()) {
            alert('Nie możesz dodawać komentarzy na swoim własnym profilu');
            return;
        }
        this.showCommentForm.update(show => !show);
    }

    onSubmitComment(content: string): void {
        const userId = this.profileUserId();
        if (!userId) return;

        // Double check - prevent commenting on own profile
        if (this.isOwnProfile()) {
            this.commentError.set('Nie możesz dodawać komentarzy na swoim własnym profilu');
            return;
        }

        this.isSubmittingComment.set(true);
        this.commentError.set(null);

        this.reviewService.createComment(userId, content).subscribe({
            next: (newComment: ProfileComment) => {
                this.isSubmittingComment.set(false);
                this.commentError.set(null);

                // Reset the form
                this.resetCommentForm.set(true);
                setTimeout(() => this.resetCommentForm.set(false), 0);

                // Close form and add the new comment to the list immediately for better UX
                this.showCommentForm.set(false);
                this.comments.update(comments => [newComment, ...comments]);
            },
            error: (error: { error?: { detail?: string | { msg: string }[] }; message?: string }) => {
                console.error('Failed to submit comment:', error);
                this.isSubmittingComment.set(false);

                // Extract error message from API response
                let errorMessage = 'Nie udało się dodać komentarza';
                if (error.error?.detail) {
                    if (typeof error.error.detail === 'string') {
                        errorMessage = error.error.detail;
                    } else if (Array.isArray(error.error.detail)) {
                        errorMessage = error.error.detail.map((e: { msg: string }) => e.msg).join(', ');
                    }
                } else if (error.message) {
                    errorMessage = error.message;
                }

                this.commentError.set(errorMessage);
            },
        });
    }

    onCancelComment(): void {
        this.showCommentForm.set(false);
        this.commentError.set(null);
    }
}
