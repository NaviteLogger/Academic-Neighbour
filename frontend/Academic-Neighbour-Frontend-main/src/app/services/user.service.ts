import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { UserRead } from '../models/auth.model';

@Injectable({
    providedIn: 'root',
})
export class UserService {
    private http = inject(HttpClient);
    private readonly apiUrl = environment.apiUrl;

    /**
     * Get current authenticated user information
     * @returns Observable of the current user
     */
    getCurrentUser(): Observable<UserRead> {
        return this.http.get<UserRead>(`${this.apiUrl}/users/me`).pipe(
            catchError(error => {
                console.error('Failed to fetch current user:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get user profile information by user ID
     * @param userId - The ID of the user
     * @returns Observable of the user profile
     */
    getUserProfile(userId: number): Observable<UserRead> {
        return this.http.get<UserRead>(`${this.apiUrl}/users/${userId}`).pipe(
            catchError(error => {
                console.error('Failed to fetch user profile:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Search for users by username, first name, or last name
     * @param query - The search query string
     * @returns Observable of matching users
     */
    searchUsers(query: string): Observable<UserRead[]> {
        return this.http.get<UserRead[]>(`${this.apiUrl}/users/search`, {
            params: { query }
        }).pipe(
            catchError(error => {
                console.error('Failed to search users:', error);
                return throwError(() => error);
            })
        );
    }
}
