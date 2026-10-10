import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ValidationErrors } from './validation-errors';

describe('ValidationErrors', () => {
  let component: ValidationErrors;
  let fixture: ComponentFixture<ValidationErrors>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ValidationErrors]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ValidationErrors);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
