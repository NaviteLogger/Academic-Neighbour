import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

export type FeedTab = 'board' | 'events' | 'groups';

@Component({
    selector: 'app-feed-tabs',
    standalone: true,
    imports: [CommonModule, MatButtonModule, MatIconModule],
    templateUrl: './feed-tabs.html',
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
