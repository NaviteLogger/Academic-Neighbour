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
  selector: 'app-friend-sent-list',
  standalone: true,
  imports: [
    CommonModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './friend-sent-list.html',
  styleUrl: './friend-sent-list.css'
})
export class FriendSentList implements OnInit {
  private friendshipService = inject(FriendshipService);

  // Sygnały do zarządzania stanem
  readonly sentRequests = signal<UserRead[]>([]);
  readonly isLoading = signal(true);
  readonly errorMessage = signal<string | null>(null);

  // Sygnały obliczeniowe
  readonly hasSentRequests = computed(() => this.sentRequests().length > 0);
  readonly isEmpty = computed(() => !this.isLoading() && !this.hasSentRequests() && !this.hasError());
  readonly hasError = computed(() => !!this.errorMessage());

  ngOnInit(): void {
    this.loadSentRequests();
  }

  loadSentRequests(): void {
    this.isLoading.set(true);
    this.errorMessage.set(null);

    this.friendshipService.getSentRequests().subscribe({
      next: (users) => {
        this.sentRequests.set(users);
        this.isLoading.set(false);
      },
      error: (err) => {
        console.error('Failed to load sent requests:', err);
        this.errorMessage.set('Nie udało się załadować wysłanych zaproszeń.');
        this.isLoading.set(false);
      }
    });
  }

  cancelRequest(addresseeId: number): void {
    // Używamy removeFriend, aby anulować wysłane zaproszenie
    this.friendshipService.removeFriend(addresseeId).subscribe({
      next: () => {
        // Po anulowaniu, usuwamy zaproszenie z listy
        this.sentRequests.update(currentRequests =>
          currentRequests.filter(req => req.id !== addresseeId)
        );
      },
      error: (err) => {
        console.error('Failed to cancel request:', err);
        this.errorMessage.set('Nie udało się anulować zaproszenia.');
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