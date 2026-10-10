import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FriendList } from './friend-list';

describe('FriendList', () => {
  let component: FriendList;
  let fixture: ComponentFixture<FriendList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FriendList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FriendList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
