import { isPlatformBrowser } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Injectable, PLATFORM_ID, computed, effect, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, catchError, tap, throwError } from 'rxjs';
import { environment } from '../../environments/environment';
import {
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    User
} from '../models/auth.model';

@Injectable({
    providedIn: 'root'
})
export class AuthService {
    private http = inject(HttpClient);
    private platformId = inject(PLATFORM_ID);
    private router = inject(Router);

    private apiUrl = environment.apiUrl;
    private readonly TOKEN_KEY = 'access_token';
    private readonly USER_KEY = 'user_data';

    private tokenSignal = signal<string | null>(null);
    private userSignal = signal<User | null>(null);

    readonly token = this.tokenSignal.asReadonly();
    readonly currentUser = this.userSignal.asReadonly();
    readonly isAuthenticated = computed(() => !!this.tokenSignal());

    constructor() {
        this.initializeAuthState();
        effect(() => {
            const token = this.tokenSignal();
            if (token && this.isTokenExpired(token)) {
                this.logout();
            }
        });
    }

    /**
     * Initialize authentication state from browser storage
     */
    private initializeAuthState(): void {
        if (isPlatformBrowser(this.platformId)) {
            const token = localStorage.getItem(this.TOKEN_KEY);
            const userData = localStorage.getItem(this.USER_KEY);

            if (token) {
                this.tokenSignal.set(token);
            }

            if (userData) {
                try {
                    this.userSignal.set(JSON.parse(userData));
                } catch (error) {
                    console.error('Failed to parse user data:', error);
                    this.clearStorage();
                }
            }
        }
    }

    /**
     * Register a new user
     */
    register(data: RegisterRequest): Observable<RegisterResponse> {
        return this.http.post<RegisterResponse>(`${this.apiUrl}/users/register`, data).pipe(
            tap(response => {
                this.setAuthData(response.access_token, response.user);
            }),
            catchError(error => {
                console.error('Registration failed:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Login user
     */
    login(data: LoginRequest): Observable<LoginResponse> {
        const formData = new URLSearchParams();
        formData.append('username', data.username);
        formData.append('password', data.password);
        formData.append('grant_type', 'password');

        return this.http.post<LoginResponse>(`${this.apiUrl}/auth/token`, formData.toString(), {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }).pipe(
            tap(response => {
                this.setAuthData(response.access_token, response.user);
            }),
            catchError(error => {
                console.error('Login failed:', error);
                return throwError(() => error);
            })
        );
    }

    /**
     * Logout user and clear authentication state
     * @param navigate - Whether to navigate after logout (default: true)
     */
    logout(navigate = true): void {
        this.clearAuthData();

        if (navigate) {
            this.router.navigate(['/']);
        }
    }

    /**
     * Get current token value (for HTTP interceptors)
     */
    getToken(): string | null {
        return this.tokenSignal();
    }

    /**
     * Set authentication data (token and user)
     */
    private setAuthData(token: string, user: User): void {
        this.tokenSignal.set(token);
        this.userSignal.set(user);

        if (isPlatformBrowser(this.platformId)) {
            localStorage.setItem(this.TOKEN_KEY, token);
            localStorage.setItem(this.USER_KEY, JSON.stringify(user));
        }
    }

    /**
     * Clear authentication data
     */
    private clearAuthData(): void {
        this.tokenSignal.set(null);
        this.userSignal.set(null);
        this.clearStorage();
    }

    /**
     * Clear browser storage (SSR-safe)
     */
    private clearStorage(): void {
        if (isPlatformBrowser(this.platformId)) {
            localStorage.removeItem(this.TOKEN_KEY);
            localStorage.removeItem(this.USER_KEY);
        }
    }

    /**
     * Check if JWT token is expired
     */
    private isTokenExpired(token: string): boolean {
        try {
            const payload = this.parseJwt(token);
            if (!payload.exp) {
                return false;
            }

            const expirationDate = new Date(payload.exp * 1000);
            return expirationDate < new Date();
        } catch (error) {
            console.error('Failed to parse token:', error);
            return true;
        }
    }

    /**
     * Parse JWT token payload
     */
    private parseJwt(token: string): { exp?: number;[key: string]: unknown } {
        try {
            const base64Url = token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(
                atob(base64)
                    .split('')
                    .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                    .join('')
            );
            return JSON.parse(jsonPayload);
        } catch {
            throw new Error('Invalid token format');
        }
    }
}
