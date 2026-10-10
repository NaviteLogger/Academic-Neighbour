import { CommonModule } from '@angular/common';
import { Component, inject, input } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { ProfileComment } from '../../../../models/review.model';
import { AuthService } from '../../../../services/auth.service';

@Component({
    selector: 'app-profile-comment-list',
    standalone: true,
    imports: [CommonModule, MatIconModule, MatButtonModule],
    templateUrl: './profile-comment-list.html',
    styleUrl: './profile-comment-list.css',
})
export class ProfileCommentListComponent {
    private authService = inject(AuthService);
    private router = inject(Router);

    readonly comments = input.required<ProfileComment[]>();
    readonly currentUser = this.authService.currentUser;

    /**
     * Get initials from author name
     */
    getInitials(name: string): string {
        if (!name) return '?';
        const parts = name.trim().split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return name[0]?.toUpperCase() || '?';
    }

    /**
     * Get relative time string
     */
    getRelativeTime(dateString: string): string {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'przed chwilą';
        if (diffMins < 60) return `${diffMins} min temu`;
        if (diffHours < 24) return `${diffHours} godz. temu`;
        if (diffDays < 7) return `${diffDays} dni temu`;

        return date.toLocaleDateString('pl-PL', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    }

    /**
     * Get gradient class for avatar
     */
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

    /**
     * Navigate to user profile
     */
    navigateToProfile(authorId: number): void {
        this.router.navigate(['/profile', authorId]);
    }
}
