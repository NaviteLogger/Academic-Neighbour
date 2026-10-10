/**
 * Friendship status enumeration matching the backend API.
 */
export enum FriendshipStatus {
    PENDING = 'pending',
    ACCEPTED = 'accepted',
    DECLINED = 'declined'
}

/**
 * Filter options for listing friends
 */
export enum FriendListFilter {
    ACCEPTED = 'accepted',
    PENDING = 'pending',
    SENT = 'sent'
}

/**
 * Friendship model from the API.
 */
export interface Friendship {
    id?: number | null;
    requester_id: number;
    addressee_id: number;
    status?: FriendshipStatus;
}

/**
 * @deprecated Use Friendship instead
 */
export type FriendshipResponse = Friendship;
