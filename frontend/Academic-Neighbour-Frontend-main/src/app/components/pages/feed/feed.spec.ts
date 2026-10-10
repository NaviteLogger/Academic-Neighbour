import { provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { Feed } from './feed';

describe('Feed', () => {
  let component: Feed;
  let fixture: ComponentFixture<Feed>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Feed],
      providers: [
        provideHttpClientTesting(),
        provideRouter([])
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Feed);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load posts on init', (done) => {
    fixture.detectChanges();
    expect(component.isLoading).toBeTrue();

    setTimeout(() => {
      expect(component.isLoading).toBeFalse();
      expect(component.posts().length).toBeGreaterThan(0);
      done();
    }, 600);
  });

  it('should create new post', () => {
    const initialLength = component.posts().length;
    component.onCreatePost({ content: 'Test post' });
    expect(component.posts().length).toBe(initialLength + 1);
    expect(component.posts()[0].content).toBe('Test post');
  });

  it('should like a post', () => {
    (component as unknown as { postsSignal: { set: (value: unknown) => void } }).postsSignal.set([
      {
        id: 1,
        text: 'Test',
        author_id: 1,
        created_at: new Date().toISOString(),
      },
    ]);
    component.onLikePost(1);
    expect(component.posts()[0]).toBeTruthy();
  });
});
