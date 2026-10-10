import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { MessagesPage } from './messages';

describe('MessagesPage', () => {
    let component: MessagesPage;
    let fixture: ComponentFixture<MessagesPage>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [MessagesPage],
            providers: [provideHttpClient(), provideRouter([])],
        }).compileComponents();

        fixture = TestBed.createComponent(MessagesPage);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });
});
