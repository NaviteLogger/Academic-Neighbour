import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FeedTabsComponent } from './feed-tabs';

describe('FeedTabsComponent', () => {
    let component: FeedTabsComponent;
    let fixture: ComponentFixture<FeedTabsComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [FeedTabsComponent],
        }).compileComponents();

        fixture = TestBed.createComponent(FeedTabsComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should have board as default active tab', () => {
        expect(component.activeTab).toBe('board');
    });

    it('should change active tab when selectTab is called', () => {
        component.selectTab('events');
        expect(component.activeTab).toBe('events');
    });

    it('should emit tabChanged event when tab is selected', () => {
        let emittedTab: string | undefined;
        component.tabChanged.subscribe((tab) => {
            emittedTab = tab;
        });

        component.selectTab('groups');
        expect(emittedTab).toBe('groups');
    });

    it('should return true for isActive when tab matches activeTab', () => {
        component.activeTab = 'events';
        expect(component.isActive('events')).toBe(true);
        expect(component.isActive('board')).toBe(false);
    });
});
