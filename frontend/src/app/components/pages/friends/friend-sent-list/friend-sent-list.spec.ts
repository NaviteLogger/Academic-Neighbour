import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FriendSentList } from './friend-sent-list';

describe('FriendSentList', () => {
  let component: FriendSentList;
  let fixture: ComponentFixture<FriendSentList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FriendSentList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FriendSentList);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
