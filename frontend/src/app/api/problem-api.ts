import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { Meta, Problem, ProblemPage, ProblemQuery, TagCount } from './models';

@Injectable({ providedIn: 'root' })
export class ProblemApi {
  private readonly http = inject(HttpClient);

  list(query: ProblemQuery): Observable<ProblemPage> {
    let params = new HttpParams();
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null && value !== '') {
        params = params.set(key, String(value));
      }
    }
    return this.http.get<ProblemPage>('/api/problems', { params });
  }

  get(contestId: string, index: string): Observable<Problem> {
    return this.http.get<Problem>(
      `/api/problems/${encodeURIComponent(contestId)}/${encodeURIComponent(index)}`,
    );
  }

  tags(): Observable<TagCount[]> {
    return this.http.get<TagCount[]>('/api/problems/tags');
  }

  meta(): Observable<Meta> {
    return this.http.get<Meta>('/api/meta');
  }
}
