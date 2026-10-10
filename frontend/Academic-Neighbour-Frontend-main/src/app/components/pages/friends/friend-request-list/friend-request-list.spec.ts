import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FriendRequestList } from './friend-request-list';

describe('FriendRequestList', () => {
  let component: FriendRequestList;
  let fixture: ComponentFixture<FriendRequestList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FriendRequestList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FriendRequestList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
