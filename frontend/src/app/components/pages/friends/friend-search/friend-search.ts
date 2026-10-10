import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Router } from '@angular/router';
import { debounceTime, distinctUntilChanged } from 'rxjs';
import { UserRead } from '../../../../models/auth.model';
import { AuthService } from '../../../../services/auth.service';
import { FriendshipService } from '../../../../services/friendship.service';
import { UserService } from '../../../../services/user.service';

@Component({
    selector: 'app-friend-search',
    standalone: true,
    imports: [
        CommonModule,
        ReactiveFormsModule,
        MatFormFieldModule,
        MatInputModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatTooltipModule,
    ],
    templateUrl: './friend-search.html',
    styleUrl: './friend-search.css',
})
export class FriendSearchComponent {
    private userService = inject(UserService);
    private friendshipService = inject(FriendshipService);
    private authService = inject(AuthService);
    private router = inject(Router);

    // Form control for search input
    searchControl = new FormControl('');

    // State
    readonly searchResults = signal<UserRead[]>([]);
    readonly isSearching = signal(false);
    readonly searchError = signal<string | null>(null);
    readonly hasSearched = signal(false);
    readonly sendingRequests = signal<Set<number>>(new Set());
    readonly existingFriendIds = signal<Set<number>>(new Set());
    readonly pendingRequestIds = signal<Set<number>>(new Set());
    readonly sentRequestIds = signal<Set<number>>(new Set());

    constructor() {
        // Load existing friends and pending requests to filter them out
        this.loadExistingRelationships();

        // Setup search with debounce
        this.searchControl.valueChanges
            .pipe(
                debounceTime(300), // Wait 300ms after user stops typing
                distinctUntilChanged() // Only emit when value actually changes
            )
            .subscribe((query) => {
                if (query && query.trim().length >= 2) {
                    this.performSearch(query.trim());
                } else {
                    this.searchResults.set([]);
                    this.hasSearched.set(false);
                    this.searchError.set(null);
                }
            });
    }

    loadExistingRelationships(): void {
        // Load accepted friends
        this.friendshipService.getAcceptedFriends().subscribe({
            next: (friends) => {
                this.existingFriendIds.set(new Set(friends.map(f => f.id)));
            },
            error: (error) => console.error('Error loading friends:', error)
        });

        // Load pending received requests
        this.friendshipService.getPendingRequests().subscribe({
            next: (requests) => {
                this.pendingRequestIds.set(new Set(requests.map(r => r.id)));
            },
            error: (error) => console.error('Error loading pending requests:', error)
        });

        // Load sent requests
        this.friendshipService.getSentRequests().subscribe({
            next: (sent) => {
                this.sentRequestIds.set(new Set(sent.map(s => s.id)));
            },
            error: (error) => console.error('Error loading sent requests:', error)
        });
    }

    performSearch(query: string): void {
        this.isSearching.set(true);
        this.searchError.set(null);
        this.hasSearched.set(true);

        this.userService.searchUsers(query).subscribe({
            next: (users) => {
                const currentUserId = this.authService.currentUser()?.id;

                // Filter out current user, existing friends, and pending requests
                const filteredUsers = users.filter(user =>
                    user.id !== currentUserId &&
                    !this.existingFriendIds().has(user.id) &&
                    !this.pendingRequestIds().has(user.id) &&
                    !this.sentRequestIds().has(user.id)
                );
                this.searchResults.set(filteredUsers);
                this.isSearching.set(false);
            },
            error: (error) => {
                console.error('Search error:', error);
                this.searchError.set('Nie udało się wyszukać użytkowników.');
                this.isSearching.set(false);
            },
        });
    }

    onSendFriendRequest(userId: number): void {
        // Add to sending set
        this.sendingRequests.update((set) => new Set(set).add(userId));

        this.friendshipService.sendFriendRequest(userId).subscribe({
            next: () => {
                // Remove from sending set
                this.sendingRequests.update((set) => {
                    const newSet = new Set(set);
                    newSet.delete(userId);
                    return newSet;
                });

                // Add to sent requests
                this.sentRequestIds.update((set) => new Set(set).add(userId));

                // Remove user from search results
                this.searchResults.update((users) =>
                    users.filter((u) => u.id !== userId)
                );
            },
            error: (error) => {
                console.error('Error sending friend request:', error);
                // Remove from sending set
                this.sendingRequests.update((set) => {
                    const newSet = new Set(set);
                    newSet.delete(userId);
                    return newSet;
                });

                // Extract error message
                let errorMsg = 'Nie udało się wysłać zaproszenia.';
                if (error.error?.detail) {
                    if (typeof error.error.detail === 'string') {
                        errorMsg = error.error.detail;
                    } else if (Array.isArray(error.error.detail)) {
                        errorMsg = error.error.detail[0]?.msg || errorMsg;
                    }
                }
                alert(errorMsg);
            },
        });
    }

    navigateToProfile(userId: number): void {
        this.router.navigate(['/profile', userId]);
    }

    getInitials(user: UserRead): string {
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

    isSendingRequest(userId: number): boolean {
        return this.sendingRequests().has(userId);
    }
}
