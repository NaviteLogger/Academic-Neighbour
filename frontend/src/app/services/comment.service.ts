import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, catchError, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { CommentRequest, CommentWithAuthor } from '../models/comment.model';

@Injectable({
    providedIn: 'root',
})
export class CommentService {
    private http = inject(HttpClient);
    private readonly apiUrl = environment.apiUrl;

    /**
     * Create a new comment on a post
     * @param postId - The ID of the post to comment on
     * @param comment - The comment content
     * @returns Observable of the created comment with author info
     */
    createComment(postId: number, comment: CommentRequest): Observable<CommentWithAuthor> {
        return this.http.post<CommentWithAuthor>(
            `${this.apiUrl}/posts/${postId}/comments`,
            comment
        ).pipe(
            catchError(error => {
                console.error('Failed to create comment:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get all comments for a specific post
     * @param postId - The ID of the post
     * @returns Observable of comments array
     */
    getPostComments(postId: number): Observable<CommentWithAuthor[]> {
        return this.http.get<CommentWithAuthor[]>(
            `${this.apiUrl}/posts/${postId}/comments`
        ).pipe(
            catchError(error => {
                console.error('Failed to fetch comments:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Update a comment
     * @param commentId - The ID of the comment to update
     * @param comment - The updated comment content
     * @returns Observable of the updated comment
     */
    updateComment(commentId: number, comment: CommentRequest): Observable<CommentWithAuthor> {
        return this.http.put<CommentWithAuthor>(
            `${this.apiUrl}/posts/comments/${commentId}`,
            comment
        ).pipe(
            catchError(error => {
                console.error('Failed to update comment:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Delete a comment
     * @param commentId - The ID of the comment to delete
     * @returns Observable that completes on success
     */
    deleteComment(commentId: number): Observable<void> {
        return this.http.delete<void>(
            `${this.apiUrl}/posts/comments/${commentId}`
        ).pipe(
            catchError(error => {
                console.error('Failed to delete comment:', error);
                return throwError(() => error);
            })
        );
    }
}
