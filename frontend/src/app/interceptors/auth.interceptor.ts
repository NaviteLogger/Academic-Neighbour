import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { EMPTY } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * HTTP Interceptor to add Bearer token to requests
 * Angular v20+ functional interceptor pattern
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
    const authService = inject(AuthService);
    const router = inject(Router);
    const token = authService.getToken();

    // Define public endpoints that don't require authentication
    const publicEndpoints = [
        '/auth/token',
        '/users/register',
        '/posts/'  // GET all posts is public
    ];

    // Check if this is a public endpoint
    const isPublicEndpoint = publicEndpoints.some(endpoint => {
        if (endpoint === '/posts/' && req.method === 'GET' && req.url.endsWith('/posts/')) {
            return true; // GET /posts/ is public
        }
        return req.url.includes(endpoint) && (endpoint !== '/posts/' || req.method === 'GET');
    });

    // If it's a protected endpoint and no token is available, redirect to login
    if (!isPublicEndpoint && !token) {
        console.warn('Protected endpoint accessed without token. Redirecting to login.');
        router.navigate(['/login'], {
            queryParams: { returnUrl: router.url, authRequired: 'true' }
        });

        // Cancel the request by returning EMPTY observable
        return EMPTY;
    }

    // If we have a token, add it to the request
    if (token) {
        req = req.clone({
            setHeaders: {
                Authorization: `Bearer ${token}`
            }
        });
    }

    return next(req);
};
