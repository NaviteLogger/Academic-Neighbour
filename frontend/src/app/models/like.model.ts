/**
 * Post like model
 */
export interface PostLike {
    id?: number | null;
    user_id: number;
    post_id: number;
    created_at?: string;
}

/**
 * Likes information response model
 */
export interface LikesInfo {
    likes_count: number;
    liked_by_current_user: boolean;
}
