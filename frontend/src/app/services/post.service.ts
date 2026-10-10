import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, catchError, forkJoin, map, of, switchMap, tap, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import { LikesInfo, PostLike } from '../models/like.model';
import { Post, PostCreate, PostWithAuthor } from '../models/post.model';
import { AuthService } from './auth.service';
import { CommentService } from './comment.service';
import { UserService } from './user.service';

@Injectable({
    providedIn: 'root',
})
export class PostService {
    private http = inject(HttpClient);
    private authService = inject(AuthService);
    private commentService = inject(CommentService);
    private userService = inject(UserService);

    private readonly apiUrl = environment.apiUrl;

    // Optional: Signal-based cache for posts (can be used by components)
    private postsCache = signal<Post[]>([]);

    /**
     * Read-only access to cached posts
     */
    readonly cachedPosts = this.postsCache.asReadonly();

    /**
     * Get all posts with likes and comments information
     * Filters out posts associated with groups (only returns wall posts)
     */
    getPosts(): Observable<Post[]> {
        return this.http.get<Post[]>(`${this.apiUrl}/posts/`).pipe(
            map(posts => posts.filter(post => !post.group_id)), // Filter out group posts
            switchMap(posts => {
                if (posts.length === 0) {
                    this.postsCache.set(posts);
                    return of(posts);
                }

                // Fetch likes info and comments count for each post
                const enrichedPosts$ = posts.map(post =>
                    this.enrichPostWithMetadata(post)
                );

                return forkJoin(enrichedPosts$).pipe(
                    tap(enrichedPosts => this.postsCache.set(enrichedPosts))
                );
            }),
            catchError(error => {
                console.error('Failed to fetch posts:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Enrich a single post with likes and comments metadata
     */
    private enrichPostWithMetadata(post: Post): Observable<Post> {
        if (!post.id) {
            return of(post);
        }

        const likesInfo$ = this.authService.isAuthenticated()
            ? this.getLikesInfo(post.id).pipe(
                catchError(() => of({ likes_count: 0, liked_by_current_user: false }))
            )
            : of({ likes_count: 0, liked_by_current_user: false });

        const comments$ = this.commentService.getPostComments(post.id).pipe(
            map(comments => comments.length),
            catchError(() => of(0))
        );

        const author$ = this.userService.getUserProfile(post.author_id).pipe(
            catchError(() => of(null))
        );

        return forkJoin({
            likes: likesInfo$,
            commentsCount: comments$,
            author: author$
        }).pipe(
            map(({ likes, commentsCount, author }) => ({
                ...post,
                likes_count: likes.likes_count,
                liked_by_current_user: likes.liked_by_current_user,
                comments_count: commentsCount,
                author_username: author?.username,
                author_first_name: author?.first_name,
                author_last_name: author?.last_name
            }))
        );
    }

    /**
     * Create a new post on the main wall (not in a group)
     * The backend automatically sets author_id from authentication
     * and sets group_id to null
     */
    createPost(postData: PostCreate): Observable<Post> {
        if (!this.authService.isAuthenticated()) {
            return throwError(() => new Error('User must be authenticated to create a post'));
        }

        // Only send content - backend handles author_id and group_id
        return this.http.post<Post>(`${this.apiUrl}/posts/`, postData).pipe(
            tap(newPost => {
                // Update cache with new post
                this.postsCache.update(posts => [newPost, ...posts]);
            }),
            catchError(error => {
                console.error('Failed to create post:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Like a post
     */
    likePost(postId: number): Observable<PostLike> {
        return this.http.post<PostLike>(`${this.apiUrl}/posts/${postId}/like`, {}).pipe(
            catchError(error => {
                console.error('Failed to like post:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Unlike a post
     */
    unlikePost(postId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/posts/${postId}/like`).pipe(
            catchError(error => {
                console.error('Failed to unlike post:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get likes information for a post
     */
    getLikesInfo(postId: number): Observable<LikesInfo> {
        return this.http.get<LikesInfo>(`${this.apiUrl}/posts/${postId}/likes`).pipe(
            catchError(error => {
                console.error('Failed to fetch likes info:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get a single post by ID
     */
    getPost(postId: number): Observable<Post> {
        return this.http.get<Post>(`${this.apiUrl}/posts/${postId}`).pipe(
            catchError(error => {
                console.error('Failed to fetch post:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get a single post by ID with author information
     */
    getPostWithAuthor(postId: number): Observable<PostWithAuthor> {
        return this.http.get<PostWithAuthor>(`${this.apiUrl}/posts/${postId}/with-author`).pipe(
            catchError(error => {
                console.error('Failed to fetch post with author:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Clear the posts cache
     */
    clearCache(): void {
        this.postsCache.set([]);
    }
}
