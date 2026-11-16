/**
 * User role enumeration
 */
export enum UserRole {
    USER = 'user',
    ADMIN = 'admin'
}

/**
 * User creation request model
 */
export interface UserCreate {
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    password: string;
}

/**
 * Login request model
 */
export interface LoginRequest {
    username: string;
    password: string;
}

/**
 * User read model (API response)
 */
export interface UserRead {
    id: number;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    role: UserRole | string;
    is_active: boolean;
    created_at: string;
}

/**
 * Token response with user information
 */
export interface TokenWithUser {
    access_token: string;
    token_type: string;
    user: UserRead;
}

export type RegisterResponse = TokenWithUser;
export type LoginResponse = TokenWithUser;
