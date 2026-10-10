import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CommentFormComponent } from './comment-form';

describe('CommentFormComponent', () => {
    let component: CommentFormComponent;
    let fixture: ComponentFixture<CommentFormComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [
                CommentFormComponent,
                ReactiveFormsModule,
                MatFormFieldModule,
                MatInputModule,
                MatButtonModule,
                BrowserAnimationsModule,
            ],
        }).compileComponents();

        fixture = TestBed.createComponent(CommentFormComponent);
        component = fixture.componentInstance;
        fixture.componentRef.setInput('postId', 1);
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should emit submitComment event when form is valid', () => {
        spyOn(component.submitComment, 'emit');
        component.commentForm.patchValue({ content: 'Test comment' });
        component.onSubmit();
        expect(component.submitComment.emit).toHaveBeenCalledWith({ content: 'Test comment' });
    });

    it('should not emit submitComment event when form is invalid', () => {
        spyOn(component.submitComment, 'emit');
        component.commentForm.patchValue({ content: '' });
        component.onSubmit();
        expect(component.submitComment.emit).not.toHaveBeenCalled();
    });
});
