import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { FeedHeaderComponent } from './feed-header';

describe('FeedHeaderComponent', () => {
    let component: FeedHeaderComponent;
    let fixture: ComponentFixture<FeedHeaderComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [FeedHeaderComponent],
            providers: [
                provideHttpClientTesting(),
                provideRouter([])
            ]
        }).compileComponents();

        fixture = TestBed.createComponent(FeedHeaderComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
