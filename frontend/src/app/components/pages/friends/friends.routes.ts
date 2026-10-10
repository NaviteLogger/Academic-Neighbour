import { Routes } from '@angular/router';
import { FriendLayout } from './friend-layout/friend-layout';
import { FriendList } from './friend-list/friend-list';
import { FriendRequestList } from './friend-request-list/friend-request-list';
import { FriendSearchComponent } from './friend-search/friend-search';
import { FriendSentList } from './friend-sent-list/friend-sent-list';

export const friendsRoutes: Routes = [
    {
        path: '',
        component: FriendLayout,
        children: [
            {
                title: 'Twoi znajomi',
                path: 'list',
                component: FriendList
            },
            {
                title: 'Otrzymane zaproszenia',
                path: 'requests',
                component: FriendRequestList
            },
            {
                title: 'Wysłane zaproszenia',
                path: 'sent',
                component: FriendSentList
            },
            {
                title: 'Szukaj znajomych',
                path: 'search',
                component: FriendSearchComponent
            },
            {
                // Domyślne przekierowanie na listę znajomych
                path: '',
                redirectTo: 'list',
                pathMatch: 'full'
            }
        ]
    }
];