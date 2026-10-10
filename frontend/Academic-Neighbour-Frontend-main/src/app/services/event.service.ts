import { HttpClient } from '@angular/common/http';
import { Injectable, inject, signal } from '@angular/core';
import { Observable, catchError, tap, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import {
    AttendanceStatus,
    Event,
    EventAttendee,
    EventAttendeeWithUser,
    EventCreate,
    EventUpdate
} from '../models/event.model';

@Injectable({
    providedIn: 'root',
})
export class EventService {
    private http = inject(HttpClient);
    private readonly apiUrl = environment.apiUrl;

    // Signal-based cache for events
    private eventsCache = signal<Event[]>([]);

    /**
     * Read-only access to cached events
     */
    readonly cachedEvents = this.eventsCache.asReadonly();

    /**
     * Get all upcoming events
     * @returns Observable of events array
     */
    getEvents(): Observable<Event[]> {
        return this.http.get<Event[]>(`${this.apiUrl}/events/`).pipe(
            tap(events => this.eventsCache.set(events)),
            catchError(error => {
                console.error('Failed to fetch events:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get a specific event by ID
     * @param eventId - The ID of the event
     * @returns Observable of the event
     */
    getEvent(eventId: number): Observable<Event> {
        return this.http.get<Event>(`${this.apiUrl}/events/${eventId}`).pipe(
            catchError(error => {
                console.error('Failed to fetch event:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Create a new event
     * @param event - The event data
     * @returns Observable of the created event
     */
    createEvent(event: EventCreate): Observable<Event> {
        return this.http.post<Event>(`${this.apiUrl}/events/`, event).pipe(
            tap(newEvent => {
                this.eventsCache.update(events => [newEvent, ...events]);
            }),
            catchError(error => {
                console.error('Failed to create event:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Update an existing event
     * @param eventId - The ID of the event to update
     * @param event - The updated event data
     * @returns Observable of the updated event
     */
    updateEvent(eventId: number, event: EventUpdate): Observable<Event> {
        return this.http.put<Event>(`${this.apiUrl}/events/${eventId}`, event).pipe(
            tap(updatedEvent => {
                this.eventsCache.update(events =>
                    events.map(e => e.id === eventId ? updatedEvent : e)
                );
            }),
            catchError(error => {
                console.error('Failed to update event:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Delete an event
     * @param eventId - The ID of the event to delete
     * @returns Observable that completes on success
     */
    deleteEvent(eventId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/events/${eventId}`).pipe(
            tap(() => {
                this.eventsCache.update(events =>
                    events.filter(e => e.id !== eventId)
                );
            }),
            catchError(error => {
                console.error('Failed to delete event:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Register for an event (initial registration as 'interested')
     * @param eventId - The ID of the event to register for
     * @returns Observable of the event attendee record
     */
    registerForEvent(eventId: number): Observable<EventAttendee> {
        return this.http.post<EventAttendee>(
            `${this.apiUrl}/events/${eventId}/register`,
            {}
        ).pipe(
            catchError(error => {
                console.error('Failed to register for event:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Update registration status for an event
     * @param eventId - The ID of the event
     * @param status - The new attendance status
     * @returns Observable of the updated event attendee record
     */
    updateRegistrationStatus(
        eventId: number,
        status: AttendanceStatus
    ): Observable<EventAttendee> {
        return this.http.put<EventAttendee>(
            `${this.apiUrl}/events/${eventId}/register`,
            null,
            {
                params: { attendance_status: status }
            }
        ).pipe(
            catchError(error => {
                console.error('Failed to update registration status:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Get attendees for a specific event
     * @param eventId - The ID of the event
     * @returns Observable of event attendees array with user details
     */
    getEventAttendees(eventId: number): Observable<EventAttendeeWithUser[]> {
        return this.http.get<EventAttendeeWithUser[]>(`${this.apiUrl}/events/${eventId}/attendees`).pipe(
            catchError(error => {
                console.error('Failed to fetch event attendees:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Unregister from an event (delete registration)
     * @param eventId - The ID of the event to unregister from
     * @returns Observable that completes on success
     */
    unregisterFromEvent(eventId: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}/events/${eventId}/register`).pipe(
            catchError(error => {
                console.error('Failed to unregister from event:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Clear the events cache
     */
    clearCache(): void {
        this.eventsCache.set([]);
    }
}
