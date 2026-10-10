import { Component, computed, inject, ChangeDetectionStrategy } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../../../services/auth.service';

@Component({
  selector: 'app-feed-header',
  standalone: true,
  imports: [RouterModule, MatIconModule, MatButtonModule, MatMenuModule, MatDividerModule],
  templateUrl: './feed-header.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './feed-header.css',
})
export class FeedHeaderComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  // Expose user data as signals
  readonly currentUser = this.authService.currentUser;

  // Computed signal for user initials
  readonly userInitials = computed(() => {
    const user = this.currentUser();
    if (!user) return 'U';

    const firstInitial = user.first_name?.[0]?.toUpperCase() || '';
    const lastInitial = user.last_name?.[0]?.toUpperCase() || '';
    return firstInitial + lastInitial || user.username?.[0]?.toUpperCase() || 'U';
  });

  // Computed signal for user display name
  readonly userDisplayName = computed(() => {
    const user = this.currentUser();
    if (!user) return 'Moje konto';

    return `${user.first_name} ${user.last_name}`.trim() || user.username || 'Moje konto';
  });

  navigateToProfile(): void {
    const user = this.currentUser();
    if (user?.id) {
      this.router.navigate(['/profile', user.id]);
    }
  }

  logout(): void {
    this.authService.logout();
  }
}
