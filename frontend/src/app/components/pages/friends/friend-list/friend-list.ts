import { CommonModule } from '@angular/common';
import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { Router } from '@angular/router';
import { UserRead } from '../../../../models/auth.model';
import { FriendshipService } from '../../../../services/friendship.service';

// Importy Angular Material
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatListModule } from '@angular/material/list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner'; // Dla ładowania
import { MatTooltipModule } from '@angular/material/tooltip'; // Dla podpowiedzi na przyciskach

@Component({
  selector: 'app-friend-list',
  standalone: true,
  imports: [
    CommonModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './friend-list.html',
  styleUrl: './friend-list.css'
})
export class FriendList implements OnInit {
  private friendshipService = inject(FriendshipService);
  private router = inject(Router);

  // Sygnały do zarządzania stanem
  readonly friends = signal<UserRead[]>([]);
  readonly isLoading = signal(true); // Zaczynamy od stanu ładowania
  readonly errorMessage = signal<string | null>(null);

  // Sygnały obliczeniowe do sprawdzania stanu
  readonly hasFriends = computed(() => this.friends().length > 0);
  readonly isEmpty = computed(() => !this.isLoading() && !this.hasFriends() && !this.hasError());
  readonly hasError = computed(() => !!this.errorMessage());

  ngOnInit(): void {
    this.loadFriends();
  }

  loadFriends(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.friendshipService.getAcceptedFriends().subscribe({
      next: (users) => {
        this.friends.set(users);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Failed to load friends:', err);
        this.errorMessage.set('Nie udało się załadować listy znajomych. Spróbuj ponownie później.');
        this.isLoading.set(false);
      }
    });
  }

  removeFriend(friendId: number): void {
    // Opcjonalnie: można dodać potwierdzenie
    this.friendshipService.removeFriend(friendId).subscribe({
      next: () => {
        // Po pomyślnym usunięciu, aktualizujemy listę w sygnale
        this.friends.update(currentFriends =>
          currentFriends.filter(friend => friend.id !== friendId)
        );
      },
      error: (err) => {
        console.error('Failed to remove friend:', err);
        // Opcjonalnie: można ustawić błąd usuwania
        this.errorMessage.set('Nie udało się usunąć znajomego.');
        // Ukryj błąd po kilku sekundach
        setTimeout(() => this.errorMessage.set(null), 3000);
      }
    });
  }

  // Funkcja pomocnicza do tworzenia inicjałów (jak w feed-header)
  getInitials(user: UserRead): string {
    const firstInitial = user.first_name?.[0]?.toUpperCase() || '';
    const lastInitial = user.last_name?.[0]?.toUpperCase() || '';
    return firstInitial + lastInitial || user.username?.[0]?.toUpperCase() || 'U';
  }

  // Navigate to user profile
  navigateToProfile(userId: number): void {
    this.router.navigate(['/profile', userId]);
  }
}