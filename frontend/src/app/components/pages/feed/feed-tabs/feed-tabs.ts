import { Component, input, output, ChangeDetectionStrategy } from '@angular/core';

import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

export type FeedTab = 'board' | 'events' | 'groups';

@Component({
  selector: 'app-feed-tabs',
  standalone: true,
  imports: [MatButtonModule, MatIconModule],
  templateUrl: './feed-tabs.html',
  changeDetection: ChangeDetectionStrategy.Eager,
  styleUrl: './feed-tabs.css',
})
export class FeedTabsComponent {
  activeTab = input<FeedTab>('board');

  tabChanged = output<FeedTab>();

  selectTab(tab: FeedTab): void {
    this.tabChanged.emit(tab);
  }

  isActive(tab: FeedTab): boolean {
    return this.activeTab() === tab;
  }
}
