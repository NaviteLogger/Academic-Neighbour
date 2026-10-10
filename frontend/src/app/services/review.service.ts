import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ProfileComment, ProfileCommentCreate } from '../models/review.model';

@Injectable({
    providedIn: 'root',
})
export class ReviewService {
    private http = inject(HttpClient);
    private apiUrl = `${environment.apiUrl}/users`;

    /**
     * Get all comments for a specific user profile
     */
    getUserComments(userId: number): Observable<ProfileComment[]> {
        return this.http.get<ProfileComment[]>(`${this.apiUrl}/${userId}/comments`);
    }

    /**
     * Create a new comment on a user profile
     */
    createComment(userId: number, content: string): Observable<ProfileComment> {
        const request: ProfileCommentCreate = { content };
        return this.http.post<ProfileComment>(`${this.apiUrl}/${userId}/comments`, request);
    }

    /**
     * Update a profile comment
     */
    updateComment(commentId: number, content: string): Observable<ProfileComment> {
        const request: ProfileCommentCreate = { content };
        return this.http.put<ProfileComment>(`${this.apiUrl}/comments/${commentId}`, request);
    }
}
