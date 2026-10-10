/**
 * Group model from the API (GroupRead schema)
 */
export interface Group {
    id: number;
    name: string;
    description: string;
    creator_id: number;
    created_at: string;
    member_count?: number;
    is_member?: boolean;
}

/**
 * Request model for creating a group
 */
export interface GroupCreate {
    name: string;
    description: string;
}
