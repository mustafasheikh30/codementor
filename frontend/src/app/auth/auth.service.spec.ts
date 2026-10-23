import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';

import { User } from '../api/models';
import { AuthService } from './auth.service';

const USER: User = {
  id: 1,
  handle: 'tester',
  rating: 1500,
  avatar: null,
};

describe('AuthService', () => {
  let service: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('loads the authenticated user from the same-origin API', () => {
    service.load();

    const req = http.expectOne('/api/auth/me');
    expect(req.request.method).toBe('GET');
    req.flush(USER);

    expect(service.user()).toEqual(USER);
    expect(service.loaded()).toBe(true);
    expect(service.loading()).toBe(false);
  });

  it('treats an unauthenticated response as signed out', () => {
    service.load();

    http
      .expectOne('/api/auth/me')
      .flush({ detail: 'Not authenticated' }, { status: 401, statusText: 'Unauthorized' });

    expect(service.user()).toBeNull();
    expect(service.loaded()).toBe(true);
    expect(service.loading()).toBe(false);
  });

  it('logs out through the API and clears the local user', () => {
    service.user.set(USER);
    service.logout();

    const req = http.expectOne('/api/auth/logout');
    expect(req.request.method).toBe('POST');
    req.flush(null, { status: 204, statusText: 'No Content' });

    expect(service.user()).toBeNull();
    expect(service.loaded()).toBe(true);
  });
});
