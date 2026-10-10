import { provideHttpClient } from '@angular/common/http';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { CommentWithAuthor } from '../../../../../models/comment.model';
import { CommentListComponent } from './comment-list';

describe('CommentListComponent', () => {
    let component: CommentListComponent;
    let fixture: ComponentFixture<CommentListComponent>;

    const mockComments: CommentWithAuthor[] = [
        {
            id: 1,
            content: 'Test comment 1',
            author_id: 1,
            author_name: 'User 1',
            post_id: 1,
            created_at: new Date().toISOString(),
        },
        {
            id: 2,
            content: 'Test comment 2',
            author_id: 2,
            author_name: 'User 2',
            post_id: 1,
            created_at: new Date().toISOString(),
        },
    ];

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                CommentListComponent,
                MatButtonModule,
                MatIconModule,
            ],
            providers: [provideHttpClient()],
        }).compileComponents();

        fixture = TestBed.createComponent(CommentListComponent);
        component = fixture.componentInstance;
        fixture.componentRef.setInput('comments', mockComments);
        fixture.componentRef.setInput('postId', 1);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should display comments', () => {
        expect(component.sortedComments().length).toBe(2);
    });

    it('should emit deleteComment event', () => {
        spyOn(component.deleteComment, 'emit');
        spyOn(window, 'confirm').and.returnValue(true);
        component.onDeleteComment(1);
        expect(component.deleteComment.emit).toHaveBeenCalledWith(1);
    });
});
