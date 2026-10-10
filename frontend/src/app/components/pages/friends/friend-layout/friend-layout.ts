import { Component } from '@angular/core';

import { RouterModule } from '@angular/router'; // Ważne dla router-outlet i routerLink
import { MatTabsModule } from '@angular/material/tabs'; // Moduł dla zakładek
import { FeedHeaderComponent } from '../../feed/feed-header/feed-header'; // Nagłówek

@Component({
  selector: 'app-friend-layout',
  imports: [RouterModule, MatTabsModule, FeedHeaderComponent],
  templateUrl: './friend-layout.html',
  styleUrl: './friend-layout.css',
})
export class FriendLayout {}
