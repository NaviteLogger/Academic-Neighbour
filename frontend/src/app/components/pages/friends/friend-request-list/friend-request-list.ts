import { Component, OnInit, signal, inject, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FriendshipService } from '../../../../services/friendship.service';
import { UserRead } from '../../../../models/auth.model';

// Importy Angular Material
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

@Component({
  selector: 'app-friend-request-list',
  standalone: true,
  imports: [
    CommonModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './friend-request-list.html',
  styleUrl: './friend-request-list.css'
})
export class FriendRequestList implements OnInit {
  private friendshipService = inject(FriendshipService);

  // Sygnały do zarządzania stanem
  readonly requests = signal<UserRead[]>([]);
  readonly isLoading = signal(true);
  readonly errorMessage = signal<string | null>(null);

  // Sygnały obliczeniowe
  readonly hasRequests = computed(() => this.requests().length > 0);
  readonly isEmpty = computed(() => !this.isLoading() && !this.hasRequests() && !this.hasError());
  readonly hasError = computed(() => !!this.errorMessage());

  ngOnInit(): void {
    this.loadRequests();
  }

  loadRequests(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.friendshipService.getPendingRequests().subscribe({
      next: (users) => {
        this.requests.set(users);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Failed to load friend requests:', err);
        this.errorMessage.set('Nie udało się załadować zaproszeń do znajomych.');
        this.isLoading.set(false);
      }
    });
  }

  acceptRequest(requesterId: number): void {
    this.friendshipService.acceptFriendRequest(requesterId).subscribe({
      next: () => {
        // Po akceptacji, usuwamy zaproszenie z listy
        this.requests.update(currentRequests =>
          currentRequests.filter(req => req.id !== requesterId)
        );
        // Idealnie byłoby też przenieść go na listę znajomych, 
        // ale to wymagałoby współdzielonego serwisu stanu. 
        // Na razie proste usunięcie z tej listy wystarczy.
      },
      error: (err) => {
        console.error('Failed to accept request:', err);
        this.errorMessage.set('Nie udało się zaakceptować zaproszenia.');
        setTimeout(() => this.errorMessage.set(null), 3000);
      }
    });
  }

  declineRequest(requesterId: number): void {
    this.friendshipService.declineFriendRequest(requesterId).subscribe({
      next: () => {
        // Po odrzuceniu, również usuwamy zaproszenie z listy
        this.requests.update(currentRequests =>
          currentRequests.filter(req => req.id !== requesterId)
        );
      },
      error: (err) => {
        console.error('Failed to decline request:', err);
        this.errorMessage.set('Nie udało się odrzucić zaproszenia.');
        setTimeout(() => this.errorMessage.set(null), 3000);
      }
    });
  }

  // Funkcja pomocnicza do tworzenia inicjałów
  getInitials(user: UserRead): string {
    const firstInitial = user.first_name?.[0]?.toUpperCase() || '';
    const lastInitial = user.last_name?.[0]?.toUpperCase() || '';
    return firstInitial + lastInitial || user.username?.[0]?.toUpperCase() || 'U';
  }
}