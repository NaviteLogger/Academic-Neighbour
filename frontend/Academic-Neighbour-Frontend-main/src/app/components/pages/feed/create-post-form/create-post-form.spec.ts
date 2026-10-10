import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ReactiveFormsModule } from '@angular/forms';
import { CreatePostFormComponent } from './create-post-form';

describe('CreatePostFormComponent', () => {
    let component: CreatePostFormComponent;
    let fixture: ComponentFixture<CreatePostFormComponent>;

    beforeEach(async () => {
        await TestBed.configureTestingModule({
            imports: [CreatePostFormComponent, ReactiveFormsModule],
        }).compileComponents();

        fixture = TestBed.createComponent(CreatePostFormComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    it('should expand form on focus', () => {
        expect(component.isExpanded).toBeFalse();
        component.onFocus();
        expect(component.isExpanded).toBeTrue();
    });

    it('should reset form on cancel', () => {
        component.postForm.patchValue({ content: 'Test content' });
        component.onFocus();
        component.onCancel();
        expect(component.isExpanded).toBeFalse();
        expect(component.postForm.value.content).toBeNull();
    });

    it('should emit createPost event on valid submit', () => {
        spyOn(component.createPost, 'emit');
        component.postForm.patchValue({ content: 'Test content' });
        component.onSubmit();
        expect(component.createPost.emit).toHaveBeenCalledWith({ content: 'Test content' });
    });

    it('should not emit createPost event on invalid submit', () => {
        spyOn(component.createPost, 'emit');
        component.postForm.patchValue({ content: '' });
        component.onSubmit();
        expect(component.createPost.emit).not.toHaveBeenCalled();
    });

    it('should calculate character count correctly', () => {
        component.postForm.patchValue({ content: 'Hello' });
        expect(component.characterCount).toBe(5);
    });
});
