import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting } from '@angular/common/http/testing';
import { signal } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { of, Subject } from 'rxjs';
import { Post } from '../../../models/post.model';
import { AuthService } from '../../../services/auth.service';
import { EventService } from '../../../services/event.service';
import { GroupService } from '../../../services/group.service';
import { PostService } from '../../../services/post.service';
import { Feed } from './feed';

describe('Feed', () => {
  let component: Feed;
  let fixture: ComponentFixture<Feed>;
  let posts$: Subject<Post[]>;

  const post: Post = {
    id: 1,
    content: 'Test',
    author_id: 1,
    created_at: new Date().toISOString(),
    liked_by_current_user: false,
  };

  const postService = {
    cachedPosts: signal<Post[]>([]),
    getPosts: vi.fn(),
    createPost: vi.fn(),
    likePost: vi.fn(),
    unlikePost: vi.fn(),
  };

  beforeEach(async () => {
    posts$ = new Subject<Post[]>();
    postService.cachedPosts.set([]);
    postService.getPosts.mockReset().mockReturnValue(posts$);
    postService.createPost.mockReset().mockReturnValue(of(post));
    postService.likePost.mockReset().mockReturnValue(of({}));
    postService.unlikePost.mockReset().mockReturnValue(of(undefined));

    await TestBed.configureTestingModule({
      imports: [Feed],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
        { provide: PostService, useValue: postService },
        { provide: EventService, useValue: { cachedEvents: signal([]), getEvents: () => of([]) } },
        { provide: GroupService, useValue: { getGroups: () => of([]) } },
      ],
    }).compileComponents();

    vi.spyOn(TestBed.inject(AuthService), 'isAuthenticated').mockReturnValue(true);

    fixture = TestBed.createComponent(Feed);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load posts on init', () => {
    expect(postService.getPosts).toHaveBeenCalled();

    postService.cachedPosts.set([post]);
    posts$.next([post]);
    posts$.complete();

    expect(component.isLoading()).toBe(false);
    expect(component.posts().length).toBeGreaterThan(0);
  });

  it('should create new post', () => {
    component.onCreatePost({ content: 'Test post' });
    expect(postService.createPost).toHaveBeenCalledWith({ content: 'Test post' });
  });

  it('should like a post', () => {
    postService.cachedPosts.set([post]);
    component.onLikePost(1);
    expect(postService.likePost).toHaveBeenCalledWith(1);
    expect(postService.unlikePost).not.toHaveBeenCalled();
  });
});
