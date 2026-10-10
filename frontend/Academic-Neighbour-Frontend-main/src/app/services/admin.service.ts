import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { UserRead } from '../models/auth.model';

@Injectable({
    providedIn: 'root',
})
export class AdminService {
    private http = inject(HttpClient);
    private readonly apiUrl = environment.apiUrl;

    /**
     * Get all users (admin only)
     * @returns Observable of users array
     */
    getAllUsers(): Observable<UserRead[]> {
        return this.http.get<UserRead[]>(`${this.apiUrl}/admin/users`).pipe(
            catchError(error => {
                console.error('Failed to fetch all users:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get a specific user by username or email (admin only)
     * @param identifier - Username or email of the user
     * @returns Observable of the user
     */
    getUserByIdentifier(identifier: string): Observable<UserRead> {
        return this.http.get<UserRead>(`${this.apiUrl}/admin/user/${identifier}`).pipe(
            catchError(error => {
                console.error('Failed to fetch user:', error);
                return throwError(() => error);
            })
        );
    }
}
