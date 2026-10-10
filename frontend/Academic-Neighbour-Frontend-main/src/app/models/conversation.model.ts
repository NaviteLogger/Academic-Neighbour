/**
 * Conversation read model from API
 */
export interface Conversation {
    id: number;
    title: string;
    created_at: string;
    participants?: { id: number; username: string; first_name: string; last_name: string }[];
    displayName?: string; // Computed display name for the current user
}

/**
 * Conversation creation request model
 */
export interface ConversationCreate {
    participant_id: number;
}

/**
 * Message read model with sender information
 */
export interface Message {
    id: number;
    content: string;
    sender_id: number;
    sender_name: string;
    conversation_id: number;
    created_at: string;
}

/**
 * Message creation request model
 */
export interface MessageCreate {
    content: string;
}
