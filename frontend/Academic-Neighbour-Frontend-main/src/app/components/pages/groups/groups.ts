import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Router } from '@angular/router';
import { Group } from '../../../models/group.model';
import { AuthService } from '../../../services/auth.service';
import { GroupService } from '../../../services/group.service';
import { FeedHeaderComponent } from '../feed/feed-header/feed-header';

@Component({
    selector: 'app-groups',
    standalone: true,
    imports: [
        CommonModule,
        MatButtonModule,
        MatCardModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatChipsModule,
        FeedHeaderComponent,
    ],
    templateUrl: './groups.html',
    styleUrl: './groups.css',
})
export class GroupsPage {
    private groupService = inject(GroupService);
    private authService = inject(AuthService);
    private router = inject(Router);

    readonly groups = signal<Group[]>([]);
    readonly isLoading = signal(false);
    readonly currentUser = this.authService.currentUser;

    constructor() {
        this.loadGroups();
    }

    loadGroups(): void {
        this.isLoading.set(true);
        this.groupService.getGroups().subscribe({
            next: (groups) => {
                this.groups.set(groups);
                this.isLoading.set(false);
            },
            error: (error) => {
                console.error('Failed to load groups:', error);
                this.isLoading.set(false);
            },
        });
    }

    navigateToGroup(groupId: number): void {
        this.router.navigate(['/groups', groupId]);
    }

    navigateToCreateGroup(): void {
        this.router.navigate(['/groups/create']);
    }

    getGroupInitials(name: string): string {
        const words = name.trim().split(' ');
        if (words.length >= 2) {
            return (words[0][0] + words[1][0]).toUpperCase();
        }
        return name.substring(0, 2).toUpperCase();
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

    getRelativeDate(dateString: string): string {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffDays === 0) return 'Dziś';
        if (diffDays === 1) return 'Wczoraj';
        if (diffDays < 7) return `${diffDays} dni temu`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} tyg. temu`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} mies. temu`;
        return `${Math.floor(diffDays / 365)} lat temu`;
    }
}
