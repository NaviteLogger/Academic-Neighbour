import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FriendLayout } from './friend-layout';

describe('FriendLayout', () => {
  let component: FriendLayout;
  let fixture: ComponentFixture<FriendLayout>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FriendLayout]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FriendLayout);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
