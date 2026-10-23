import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { AuthApi } from './auth-api';

describe('AuthApi', () => {
  let api: AuthApi;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    api = TestBed.inject(AuthApi);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('loads and toggles solved status with the expected endpoints', () => {
    api.solvedList().subscribe((list) => expect(list).toEqual([{ contest_id: 4, index: 'A' }]));
    http.expectOne('/api/users/me/solved').flush([{ contest_id: 4, index: 'A' }]);

    api.markSolved(4, 'A').subscribe((s) => expect(s.solved).toBe(true));
    const mark = http.expectOne('/api/problems/4/A/solved');
    expect(mark.request.method).toBe('POST');
    mark.flush({ solved: true });

    api.unmarkSolved(4, 'A').subscribe((s) => expect(s.solved).toBe(false));
    const unmark = http.expectOne('/api/problems/4/A/solved');
    expect(unmark.request.method).toBe('DELETE');
    unmark.flush({ solved: false });
  });

  it('encodes problem indexes in URLs', () => {
    api.getSolvedStatus(100, 'A1').subscribe();
    http.expectOne('/api/problems/100/A1/solved').flush({ solved: false });
  });

  it('loads the progress summary from the API', () => {
    const body = { solved_count: 2, by_difficulty: [{ rating: 800, count: 2 }] };
    api.progress().subscribe((progress) => expect(progress).toEqual(body));
    http.expectOne('/api/users/me/progress').flush(body);
  });
});
