import { CommonModule } from '@angular/common';
import { HttpErrorResponse } from '@angular/common/http';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router } from '@angular/router';
import { User } from '../../../models/auth.model';
import { Group } from '../../../models/group.model';
import { Post, PostCreate } from '../../../models/post.model';
import { AuthService } from '../../../services/auth.service';
import { GroupService } from '../../../services/group.service';
import { PostService } from '../../../services/post.service';
import { CreatePostFormComponent } from '../feed/create-post-form/create-post-form';
import { FeedHeaderComponent } from '../feed/feed-header/feed-header';
import { PostComponent } from '../feed/post/post';

@Component({
    selector: 'app-group-detail',
    standalone: true,
    imports: [
        CommonModule,
        MatIconModule,
        MatButtonModule,
        MatChipsModule,
        MatProgressSpinnerModule,
        FeedHeaderComponent,
        CreatePostFormComponent,
        PostComponent,
    ],
    templateUrl: './group-detail.html',
    styleUrl: './group-detail.css',
})
export class GroupDetailPage implements OnInit {
    private groupService = inject(GroupService);
    private postService = inject(PostService);
    private authService = inject(AuthService);
    private route = inject(ActivatedRoute);
    private router = inject(Router);

    // State
    readonly group = signal<Group | null>(null);
    readonly posts = signal<Post[]>([]);
    readonly members = signal<User[]>([]);
    readonly isLoading = signal(true);
    readonly isLoadingPosts = signal(false);
    readonly isLoadingMembers = signal(false);
    readonly errorMessage = signal<string | null>(null);
    readonly isRedirecting = signal(false);
    readonly showMembers = signal(false);

    // Computed
    readonly groupId = computed(() => this.group()?.id);
    readonly isCreator = computed(() => {
        const userId = this.authService.currentUser()?.id;
        return userId === this.group()?.creator_id;
    });
    readonly isMember = computed(() => this.group()?.is_member || false);
    readonly hasPosts = computed(() => this.posts().length > 0);
    readonly hasError = computed(() => !!this.errorMessage());

    ngOnInit(): void {
        this.route.params.subscribe(params => {
            const id = Number(params['id']);
            if (id) {
                this.loadGroup(id);
                this.loadGroupPosts(id);
            }
        });
    }

    loadGroup(groupId: number): void {
        this.isLoading.set(true);
        this.errorMessage.set(null);

        this.groupService.getGroup(groupId).subscribe({
            next: (group) => {
                this.group.set(group);
                this.loadMembers(groupId);
                this.isLoading.set(false);
            },
            error: (error) => {
                console.error('Error loading group:', error);
                this.handleError(error, 'Nie udało się załadować grupy.');
                this.isLoading.set(false);
            },
        });
    }

    loadGroupPosts(groupId: number): void {
        this.isLoadingPosts.set(true);

        this.groupService.getGroupPosts(groupId).subscribe({
            next: (posts) => {
                // Convert PostWithAuthor to Post format
                const postsData = posts.map(p => ({
                    id: p.id,
                    content: p.content,
                    author_id: p.author_id,
                    group_id: groupId,
                    created_at: p.created_at,
                    likes_count: 0,
                    comments_count: 0,
                    liked_by_current_user: false,
                }));
                this.posts.set(postsData);
                this.isLoadingPosts.set(false);
            },
            error: (error) => {
                console.error('Error loading group posts:', error);
                this.isLoadingPosts.set(false);
            },
        });
    }

    loadMembers(groupId: number): void {
        this.isLoadingMembers.set(true);

        this.groupService.getGroupMembers(groupId).subscribe({
            next: (members) => {
                this.members.set(members);
                // Update group membership status
                const currentUserId = this.authService.currentUser()?.id;
                if (this.group()) {
                    this.group.update(g => g ? {
                        ...g,
                        member_count: members.length,
                        is_member: members.some(m => m.id === currentUserId)
                    } : null);
                }
                this.isLoadingMembers.set(false);
            },
            error: (error) => {
                console.error('Error loading members:', error);
                this.isLoadingMembers.set(false);
            },
        });
    }

    onCreatePost(postData: PostCreate): void {
        const gId = this.groupId();
        if (!gId) return;

        if (!this.authService.isAuthenticated()) {
            this.redirectToLogin('Musisz być zalogowany, aby utworzyć post.');
            return;
        }

        if (!this.isMember()) {
            this.errorMessage.set('Musisz być członkiem grupy, aby dodać post.');
            return;
        }

        this.groupService.createGroupPost(gId, postData.content).subscribe({
            next: () => {
                this.loadGroupPosts(gId);
                this.errorMessage.set(null);
            },
            error: (error) => {
                console.error('Error creating post:', error);
                this.handleError(error, 'Nie udało się utworzyć posta.');
            },
        });
    }

    onJoinGroup(): void {
        const gId = this.groupId();
        if (!gId) return;

        if (!this.authService.isAuthenticated()) {
            this.redirectToLogin('Musisz być zalogowany, aby dołączyć do grupy.');
            return;
        }

        this.groupService.joinGroup(gId).subscribe({
            next: () => {
                this.loadMembers(gId);
                this.errorMessage.set(null);
            },
            error: (error) => {
                console.error('Error joining group:', error);
                this.handleError(error, 'Nie udało się dołączyć do grupy.');
            },
        });
    }

    onLeaveGroup(): void {
        const gId = this.groupId();
        if (!gId) return;

        if (!this.authService.isAuthenticated()) {
            this.redirectToLogin('Musisz być zalogowany, aby opuścić grupę.');
            return;
        }

        this.groupService.leaveGroup(gId).subscribe({
            next: () => {
                this.loadMembers(gId);
                this.errorMessage.set(null);
            },
            error: (error) => {
                console.error('Error leaving group:', error);
                this.handleError(error, 'Nie udało się opuścić grupy.');
            },
        });
    }

    toggleMembersView(): void {
        this.showMembers.update(show => !show);
    }

    onLikePost(postId: number): void {
        if (!this.authService.isAuthenticated()) {
            this.redirectToLogin('Musisz być zalogowany, aby polubić post.');
            return;
        }

        const post = this.posts().find(p => p.id === postId);
        if (!post) return;

        const isLiked = post.liked_by_current_user;

        if (isLiked) {
            this.postService.unlikePost(postId).subscribe({
                next: () => {
                    const gId = this.groupId();
                    if (gId) this.loadGroupPosts(gId);
                },
                error: (error: HttpErrorResponse) => {
                    console.error('Error unliking post:', error);
                    this.handleError(error, 'Nie udało się usunąć polubienia.');
                },
            });
        } else {
            this.postService.likePost(postId).subscribe({
                next: () => {
                    const gId = this.groupId();
                    if (gId) this.loadGroupPosts(gId);
                },
                error: (error: HttpErrorResponse) => {
                    console.error('Error liking post:', error);
                    this.handleError(error, 'Nie udało się polubić posta.');
                },
            });
        }
    }

    onRefreshPost(): void {
        const gId = this.groupId();
        if (gId) this.loadGroupPosts(gId);
    }

    navigateToProfile(userId: number): void {
        this.router.navigate(['/profile', userId]);
    }

    goBack(): void {
        this.router.navigate(['/feed']);
    }

    getInitials(user: User): string {
        const firstInitial = user.first_name?.[0]?.toUpperCase() || '';
        const lastInitial = user.last_name?.[0]?.toUpperCase() || '';
        return firstInitial + lastInitial || user.username?.[0]?.toUpperCase() || 'U';
    }

    getGradientClass(index: number): string {
        const gradients = [
            'bg-linear-to-br from-amber-400 to-pink-500',
            'bg-linear-to-br from-blue-400 to-purple-500',
            'bg-linear-to-br from-green-400 to-teal-500',
            'bg-linear-to-br from-red-400 to-orange-500',
            'bg-linear-to-br from-indigo-400 to-pink-500',
        ];
        return gradients[index % gradients.length];
    }

    private handleError(error: HttpErrorResponse, defaultMessage: string): void {
        if (error.status === 401 || error.status === 403) {
            this.redirectToLogin('Twoja sesja wygasła. Zaloguj się ponownie.');
        } else if (error.status === 0) {
            this.errorMessage.set('Brak połączenia z serwerem. Sprawdź połączenie internetowe.');
        } else if (error.status >= 500) {
            this.errorMessage.set('Serwer jest obecnie niedostępny. Spróbuj ponownie za chwilę.');
        } else {
            this.errorMessage.set(defaultMessage);
        }
    }

    private redirectToLogin(message: string): void {
        console.warn('Unauthorized action:', message);
        this.errorMessage.set(message);
        this.isRedirecting.set(true);

        setTimeout(() => {
            this.router.navigate(['/login']);
        }, 2000);
    }
}
