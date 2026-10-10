import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { protectedRoutes } from './routes/protected.routes';
import { publicRoutes } from './routes/public.routes';

export const routes: Routes = [
    // Default root route
    {
        path: '',
        redirectTo: 'home',
        pathMatch: 'full'
    },

    // Public routes
    ...publicRoutes,

    // Protected routes (requires authentication)
    {
        path: '',
        canActivate: [authGuard],
        children: protectedRoutes
    },

    // Wildcard
    { path: '**', redirectTo: 'home', pathMatch: 'full' },
];