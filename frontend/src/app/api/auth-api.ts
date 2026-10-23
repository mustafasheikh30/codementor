import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { SolvedCount, SolvedEntry, SolvedStatus, User, UserProgress } from './models';

@Injectable({ providedIn: 'root' })
export class AuthApi {
  private readonly http = inject(HttpClient);

  me(): Observable<User> {
    return this.http.get<User>('/api/auth/me');
  }

  logout(): Observable<void> {
    return this.http.post<void>('/api/auth/logout', {});
  }

  login(returnTo: string = '/problemset'): void {
    const url = new URL('/api/auth/login', window.location.origin);
    url.searchParams.set('return_to', returnTo);
    window.location.href = url.toString();
  }

  solvedList(): Observable<SolvedEntry[]> {
    return this.http.get<SolvedEntry[]>('/api/users/me/solved');
  }

  solvedCount(): Observable<SolvedCount> {
    return this.http.get<SolvedCount>('/api/users/me/solved/count');
  }

  progress(): Observable<UserProgress> {
    return this.http.get<UserProgress>('/api/users/me/progress');
  }

  getSolvedStatus(contestId: number, index: string): Observable<SolvedStatus> {
    return this.http.get<SolvedStatus>(
      `/api/problems/${contestId}/${encodeURIComponent(index)}/solved`,
    );
  }

  markSolved(contestId: number, index: string): Observable<SolvedStatus> {
    return this.http.post<SolvedStatus>(
      `/api/problems/${contestId}/${encodeURIComponent(index)}/solved`,
      {},
    );
  }

  unmarkSolved(contestId: number, index: string): Observable<SolvedStatus> {
    return this.http.delete<SolvedStatus>(
      `/api/problems/${contestId}/${encodeURIComponent(index)}/solved`,
    );
  }
}
