export interface Post {
    id?: number | null;
    content: string;
    author_id: number;
    author_username?: string;
    author_first_name?: string;
    author_last_name?: string;
    group_id?: number | null;
    created_at?: string;
    likes_count?: number;
    comments_count?: number;
    liked_by_current_user?: boolean;
}

/**
 * Post creation request model
 */
export interface PostCreate {
    content: string;
}

/**
 * Post with author details response model
 */
export interface PostWithAuthor {
    id: number;
    content: string;
    author_id: number;
    group_id?: number | null;
    created_at: string;
    author_name: string;
}

/**
 * @deprecated Use PostCreate instead
 */
export interface CreatePostDto {
    content: string;
}
