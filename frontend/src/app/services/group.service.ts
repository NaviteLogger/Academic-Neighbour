import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable, forkJoin, map, of, switchMap } from 'rxjs';
import { environment } from '../../environments/environment';
import { User } from '../models/auth.model';
import { Group, GroupCreate } from '../models/group.model';
import { PostWithAuthor } from '../models/post.model';
import { AuthService } from './auth.service';

@Injectable({
    providedIn: 'root',
})
export class GroupService {
    private http = inject(HttpClient);
    private authService = inject(AuthService);
    private apiUrl = `${environment.apiUrl}/groups`;

    /**
     * Get all groups with membership information
     */
    getGroups(): Observable<Group[]> {
        return this.http.get<Group[]>(this.apiUrl).pipe(
            switchMap(groups => {
                if (!this.authService.isAuthenticated() || groups.length === 0) {
                    return of(groups);
                }

                const currentUserId = this.authService.currentUser()?.id;

                // Enrich each group with member count and membership status
                const enrichedGroups$ = groups.map(group =>
                    this.getGroupMembers(group.id).pipe(
                        map(members => ({
                            ...group,
                            member_count: members.length,
                            is_member: members.some(member => member.id === currentUserId)
                        }))
                    )
                );

                return forkJoin(enrichedGroups$);
            })
        );
    }

    /**
     * Get a specific group by ID
     */
    getGroup(groupId: number): Observable<Group> {
        return this.http.get<Group>(`${this.apiUrl}/${groupId}`);
    }

    /**
     * Create a new group
     */
    createGroup(group: GroupCreate): Observable<Group> {
        return this.http.post<Group>(this.apiUrl, group);
    }

    /**
     * Join a group
     */
    joinGroup(groupId: number): Observable<void> {
        return this.http.post<void>(`${this.apiUrl}/${groupId}/join`, {});
    }

    /**
     * Leave a group
     */
    leaveGroup(groupId: number): Observable<void> {
        return this.http.post<void>(`${this.apiUrl}/${groupId}/leave`, {});
    }

    /**
     * Get members of a group
     */
    getGroupMembers(groupId: number): Observable<User[]> {
        return this.http.get<User[]>(`${this.apiUrl}/${groupId}/members`);
    }

    /**
     * Get posts for a specific group
     */
    getGroupPosts(groupId: number): Observable<PostWithAuthor[]> {
        return this.http.get<PostWithAuthor[]>(`${this.apiUrl}/${groupId}/posts`);
    }

    /**
     * Create a post within a group
     */
    createGroupPost(groupId: number, content: string): Observable<PostWithAuthor> {
        return this.http.post<PostWithAuthor>(`${this.apiUrl}/${groupId}/posts`, { content });
    }
}
