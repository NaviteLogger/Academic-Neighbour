import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { UserRead } from '../models/auth.model';
import { FriendListFilter, Friendship } from '../models/friendship.model';

@Injectable({
    providedIn: 'root',
})
export class FriendshipService {
    private http = inject(HttpClient);
    private readonly apiUrl = environment.apiUrl;

    /**
     * Send a friend request to a user.
     * @param addresseeId - The ID of the user to send the friend request to
     * @returns Observable of the created friendship
     */
    sendFriendRequest(addresseeId: number): Observable<Friendship> {
        return this.http.post<Friendship>(
            `${this.apiUrl}/friendships/request/${addresseeId}`,
            {}
        ).pipe(
            catchError(error => {
                console.error('Failed to send friend request:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Accept a friend request from a user.
     * @param requesterId - The ID of the user who sent the friend request
     * @returns Observable of the updated friendship
     */
    acceptFriendRequest(requesterId: number): Observable<Friendship> {
        return this.http.post<Friendship>(
            `${this.apiUrl}/friendships/accept/${requesterId}`,
            {}
        ).pipe(
            catchError(error => {
                console.error('Failed to accept friend request:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Decline a friend request from a user.
     * @param requesterId - The ID of the user who sent the friend request
     * @returns Observable of the updated friendship
     */
    declineFriendRequest(requesterId: number): Observable<Friendship> {
        return this.http.post<Friendship>(
            `${this.apiUrl}/friendships/decline/${requesterId}`,
            {}
        ).pipe(
            catchError(error => {
                console.error('Failed to decline friend request:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Remove a friend (delete friendship).
     * @param friendId - The ID of the friend to remove
     * @returns Observable that completes on success
     */
    removeFriend(friendId: number): Observable<void> {
        return this.http.delete<void>(
            `${this.apiUrl}/friendships/remove/${friendId}`
        ).pipe(
            catchError(error => {
                console.error('Failed to remove friend:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get a list of friends based on filter type.
     * @param filter - Filter type: 'accepted' (default), 'pending', or 'sent'
     * @returns Observable of user list
     */
    getFriends(filter: FriendListFilter = FriendListFilter.ACCEPTED): Observable<UserRead[]> {
        return this.http.get<UserRead[]>(`${this.apiUrl}/friendships/`, {
            params: { filter_type: filter }
        }).pipe(
            catchError(error => {
                console.error('Failed to fetch friends:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get a list of accepted friends.
     * @returns Observable of user list
     */
    getAcceptedFriends(): Observable<UserRead[]> {
        return this.getFriends(FriendListFilter.ACCEPTED);
    }

    /**
     * Get a list of received pending friend requests.
     * @returns Observable of user list who sent friend requests
     */
    getPendingRequests(): Observable<UserRead[]> {
        return this.getFriends(FriendListFilter.PENDING);
    }

    /**
     * Get a list of sent pending friend requests.
     * @returns Observable of user list to whom requests were sent
     */
    getSentRequests(): Observable<UserRead[]> {
        return this.getFriends(FriendListFilter.SENT);
    }
}
