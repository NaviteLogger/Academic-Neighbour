import { Routes } from '@angular/router';

export const protectedRoutes: Routes = [
    {
        title: 'Feed',
        path: 'feed',
        loadComponent: () => import('../components/pages/feed/feed').then(m => m.Feed)
    },
    {
        title: 'Znajomi',
        path: 'friends',
        // Ta linia ładuje nasz nowy moduł routingu dla znajomych
        loadChildren: () => import('../components/pages/friends/friends.routes').then(m => m.friendsRoutes)
    },
    {
        title: 'Wiadomości',
        path: 'messages',
        loadComponent: () => import('../components/pages/messages/messages').then(m => m.MessagesPage)
    },
    {
        title: 'Profil',
        path: 'profile/:id',
        loadComponent: () => import('../components/pages/profile/profile').then(m => m.ProfilePage)
    },
    {
        title: 'Grupy',
        path: 'groups',
        loadComponent: () => import('../components/pages/groups/groups').then(m => m.GroupsPage)
    },
    {
        title: 'Grupa',
        path: 'group/:id',
        loadComponent: () => import('../components/pages/group-detail/group-detail').then(m => m.GroupDetailPage)
    },
    {
        title: 'Event',
        path: 'event/:id',
        loadComponent: () => import('../components/pages/event-detail/event-detail').then(m => m.EventDetailPage)
    },
    {
        path: '',
        redirectTo: 'feed',
        pathMatch: 'full'
    },
];