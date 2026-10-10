import { ComponentFixture, TestBed } from '@angular/core/testing';
import { PostComponent } from './post';

describe('PostComponent', () => {
  let component: PostComponent;
  let fixture: ComponentFixture<PostComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PostComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PostComponent);
    component = fixture.componentInstance;
    fixture.componentRef.setInput('post', {
      id: 1,
      text: 'Test content',
      author_id: 1,
      created_at: new Date().toISOString(),
    });
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display post content', () => {
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Test content');
  });

  it('should emit likePost event when like button is clicked', () => {
    vi.spyOn(component.likePost, 'emit').mockReturnValue(undefined);
    component.onLike();
    expect(component.likePost.emit).toHaveBeenCalledWith(1);
  });

  it('should load comments when comments are toggled open', () => {
    vi.spyOn(component, 'loadComments').mockReturnValue(undefined);
    component.onToggleComments();
    expect(component.showComments()).toBe(true);
    expect(component.loadComments).toHaveBeenCalled();
  });
});
