/**
 * Attendance status enumeration for events
 */
export enum AttendanceStatus {
    ATTENDING = 'attending',
    INTERESTED = 'interested',
    NOT_ATTENDING = 'not_attending'
}

/**
 * Event model
 */
export interface Event {
    id?: number | null;
    title: string;
    description: string;
    location: string;
    start_date: string;
    end_date: string;
    creator_id: number;
    created_at?: string;
}

/**
 * Event creation request model
 */
export interface EventCreate {
    title: string;
    description: string;
    location: string;
    start_date: string;
    end_date: string;
}

/**
 * Event update request model
 */
export interface EventUpdate {
    title?: string | null;
    description?: string | null;
    location?: string | null;
    start_date?: string | null;
    end_date?: string | null;
}

/**
 * Event attendee model
 */
export interface EventAttendee {
    id?: number | null;
    user_id: number;
    event_id: number;
    status?: AttendanceStatus;
    joined_at?: string;
}

/**
 * Event attendee with user details (for displaying attendee lists)
 */
export interface EventAttendeeWithUser {
    user: {
        id: number;
        username: string;
        email: string;
        first_name: string;
        last_name: string;
        role: string;
        is_active: boolean;
        created_at: string;
    };
    status: AttendanceStatus;
    joined_at: string;
}
