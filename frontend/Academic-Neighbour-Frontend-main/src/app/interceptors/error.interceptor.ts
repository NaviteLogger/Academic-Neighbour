import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from '../services/auth.service';

/**
 * HTTP Interceptor to handle authentication errors globally
 * Angular v20+ functional interceptor pattern
 */
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
    const router = inject(Router);
    const authService = inject(AuthService);

    return next(req).pipe(
        catchError((error: HttpErrorResponse) => {
            if (error.status === 401 || error.status === 403) {
                console.warn('Authentication error detected:', error.status);

                authService.logout(false);

                const currentUrl = router.url;
                router.navigate(['/login'], {
                    queryParams: {
                        returnUrl: currentUrl !== '/login' ? currentUrl : '/feed',
                        sessionExpired: 'true'
                    }
                });
            }
            return throwError(() => error);
        })
    );
};
