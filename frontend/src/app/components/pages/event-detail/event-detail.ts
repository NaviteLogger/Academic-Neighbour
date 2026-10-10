import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatChipsModule } from '@angular/material/chips';
import { MatDivider } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ActivatedRoute, Router } from '@angular/router';
import { AttendanceStatus, Event, EventAttendeeWithUser } from '../../../models/event.model';
import { AuthService } from '../../../services/auth.service';
import { EventService } from '../../../services/event.service';

@Component({
    selector: 'app-event-detail',
    standalone: true,
    imports: [
        CommonModule,
        MatButtonModule,
        MatIconModule,
        MatProgressSpinnerModule,
        MatMenuModule,
        MatChipsModule,
        MatDivider
    ],
    templateUrl: './event-detail.html',
    styleUrl: './event-detail.css'
})
export class EventDetailPage implements OnInit {
    private eventService = inject(EventService);
    private authService = inject(AuthService);
    private route = inject(ActivatedRoute);
    private router = inject(Router);

    // State
    event = signal<Event | null>(null);
    attendees = signal<EventAttendeeWithUser[]>([]);
    isLoading = signal<boolean>(false);
    isLoadingAttendees = signal<boolean>(false);
    isRegistering = signal<boolean>(false);
    showAttendees = signal<boolean>(false);
    errorMessage = signal<string>('');

    // Current user
    readonly currentUser = this.authService.currentUser;

    // Computed values
    readonly isCreator = computed(() => {
        const event = this.event();
        const user = this.currentUser();
        return event && user && event.creator_id === user.id;
    });

    readonly userAttendance = computed(() => {
        const user = this.currentUser();
        const attendeesList = this.attendees();
        if (!user) return null;
        return attendeesList.find(a => a.user.id === user.id);
    });

    readonly isAttending = computed(() => {
        const attendance = this.userAttendance();
        return attendance?.status === AttendanceStatus.ATTENDING;
    });

    readonly isInterested = computed(() => {
        const attendance = this.userAttendance();
        return attendance?.status === AttendanceStatus.INTERESTED;
    });

    readonly isRegistered = computed(() => {
        const attendance = this.userAttendance();
        // User is only registered if they have ATTENDING or INTERESTED status
        return attendance?.status === AttendanceStatus.ATTENDING ||
            attendance?.status === AttendanceStatus.INTERESTED;
    });

    readonly attendingCount = computed(() => {
        return this.attendees().filter(a => a.status === AttendanceStatus.ATTENDING).length;
    });

    readonly interestedCount = computed(() => {
        return this.attendees().filter(a => a.status === AttendanceStatus.INTERESTED).length;
    });

    readonly attendingUsers = computed(() => {
        return this.attendees().filter(a => a.status === AttendanceStatus.ATTENDING);
    });

    readonly interestedUsers = computed(() => {
        return this.attendees().filter(a => a.status === AttendanceStatus.INTERESTED);
    });

    // Expose enum to template
    readonly AttendanceStatus = AttendanceStatus;

    ngOnInit(): void {
        const eventId = Number(this.route.snapshot.paramMap.get('id'));
        if (eventId) {
            this.loadEvent(eventId);
            this.loadAttendees(eventId);
        }
    }

    /**
     * Load event details
     */
    private loadEvent(eventId: number): void {
        this.isLoading.set(true);
        this.eventService.getEvent(eventId).subscribe({
            next: (event) => {
                this.event.set(event);
                this.isLoading.set(false);
            },
            error: (error) => {
                console.error('Error loading event:', error);
                this.errorMessage.set('Nie udało się załadować eventu');
                this.isLoading.set(false);
            }
        });
    }

    /**
     * Load event attendees
     */
    private loadAttendees(eventId: number): void {
        this.isLoadingAttendees.set(true);
        this.eventService.getEventAttendees(eventId).subscribe({
            next: (attendees) => {
                console.log('Loaded attendees:', attendees);
                this.attendees.set(attendees);
                this.isLoadingAttendees.set(false);
            },
            error: (error) => {
                console.error('Error loading attendees:', error);
                this.isLoadingAttendees.set(false);
                // If endpoint doesn't exist yet, initialize with empty array
                if (error.status === 404) {
                    console.warn('Attendees endpoint not implemented yet');
                    this.attendees.set([]);
                }
            }
        });
    }

    /**
     * Register for event (as interested)
     */
    onRegisterForEvent(): void {
        const event = this.event();
        if (!event?.id) return;

        this.isRegistering.set(true);
        this.eventService.registerForEvent(event.id).subscribe({
            next: (attendee) => {
                console.log('Successfully registered:', attendee);
                this.isRegistering.set(false);
                // Reload attendees to show updated list
                this.loadAttendees(event.id!);
            },
            error: (error) => {
                console.error('Error registering for event:', error);
                this.isRegistering.set(false);

                // Show more specific error message
                let errorMsg = 'Nie udało się zarejestrować na event';
                if (error.status === 400) {
                    errorMsg = 'Jesteś już zarejestrowany na ten event';
                } else if (error.status === 401) {
                    errorMsg = 'Musisz być zalogowany, aby się zarejestrować';
                } else if (error.status === 404) {
                    errorMsg = 'Event nie został znaleziony';
                } else if (error.error?.detail) {
                    errorMsg = error.error.detail;
                }

                alert(errorMsg);
            }
        });
    }

    /**
     * Update attendance status
     */
    onUpdateStatus(status: AttendanceStatus): void {
        const event = this.event();
        if (!event?.id) return;

        this.isRegistering.set(true);
        this.eventService.updateRegistrationStatus(event.id, status).subscribe({
            next: (attendee) => {
                console.log('Successfully updated status:', attendee);
                this.isRegistering.set(false);
                // Reload attendees to show updated list
                this.loadAttendees(event.id!);
            },
            error: (error) => {
                console.error('Error updating status:', error);
                this.isRegistering.set(false);

                let errorMsg = 'Nie udało się zaktualizować statusu';
                if (error.error?.detail) {
                    errorMsg = error.error.detail;
                }

                alert(errorMsg);
            }
        });
    }

    /**
     * Unregister from event (set status to NOT_ATTENDING)
     */
    onUnregisterFromEvent(): void {
        const event = this.event();
        if (!event?.id) return;

        if (!confirm('Czy na pewno chcesz wypisać się z tego eventu?')) {
            return;
        }

        this.isRegistering.set(true);
        // Update status to NOT_ATTENDING to effectively "leave" the event
        this.eventService.updateRegistrationStatus(event.id, AttendanceStatus.NOT_ATTENDING).subscribe({
            next: () => {
                console.log('Successfully unregistered from event');
                this.isRegistering.set(false);
                // Reload attendees to show updated list (user will no longer appear)
                this.loadAttendees(event.id!);
            },
            error: (error) => {
                console.error('Error unregistering from event:', error);
                this.isRegistering.set(false);

                let errorMsg = 'Nie udało się wypisać z eventu';
                if (error.error?.detail) {
                    errorMsg = error.error.detail;
                }

                alert(errorMsg);
            }
        });
    }

    /**
     * Toggle attendees list visibility
     */
    onToggleAttendees(): void {
        this.showAttendees.update(show => !show);
    }

    /**
     * Navigate back to feed
     */
    onGoBack(): void {
        this.router.navigate(['/feed'], { queryParams: { tab: 'events' } });
    }

    /**
     * Format date for display
     */
    formatDate(dateString: string): string {
        const date = new Date(dateString);
        return date.toLocaleDateString('pl-PL', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Get initials from name
     */
    getInitials(name: string): string {
        return name
            .split(' ')
            .map(n => n[0])
            .join('')
            .toUpperCase()
            .substring(0, 2);
    }

    /**
     * Get gradient class for avatar
     */
    getGradientClass(index: number): string {
        const gradients = [
            'bg-gradient-to-br from-amber-400 to-orange-500',
            'bg-gradient-to-br from-pink-400 to-rose-500',
            'bg-gradient-to-br from-purple-400 to-indigo-500',
            'bg-gradient-to-br from-blue-400 to-cyan-500',
            'bg-gradient-to-br from-green-400 to-emerald-500',
            'bg-gradient-to-br from-yellow-400 to-amber-500'
        ];
        return gradients[index % gradients.length];
    }
}
