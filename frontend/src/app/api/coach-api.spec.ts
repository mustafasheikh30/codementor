import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { CoachApi } from './coach-api';

describe('CoachApi', () => {
  let api: CoachApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(CoachApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('posts the code and hint level for the selected problem', () => {
    api.hint(4, 'A', 'print(1)', 2).subscribe((response) => {
      expect(response.hint).toBe('Consider parity.');
    });

    const req = http.expectOne('/api/coach/hint?contest_id=4&index=A');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ code: 'print(1)', level: 2 });
    req.flush({ hint: 'Consider parity.' });
  });
});
