/**
 * Comment request model for creating/updating comments
 */
export interface CommentRequest {
    content: string;
}

/**
 * Comment response model with author details
 */
export interface CommentWithAuthor {
    id: number;
    content: string;
    author_id: number;
    created_at: string;
    author_name: string;
    post_id: number;
}
