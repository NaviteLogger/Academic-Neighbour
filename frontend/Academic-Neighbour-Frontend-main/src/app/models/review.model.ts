/**
 * Profile comment from the API (ProfileCommentWithAuthor schema)
 */
export interface ProfileComment {
    id: number;
    content: string;
    author_id: number;
    author_name: string;
    profile_user_id: number;
    created_at: string;
}

/**
 * Request model for creating/updating profile comments
 */
export interface ProfileCommentCreate {
    content: string;
}
