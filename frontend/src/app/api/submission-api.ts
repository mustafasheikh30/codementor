import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { Submission, SubmissionDetail, SubmissionPage } from './models';

@Injectable({ providedIn: 'root' })
export class SubmissionApi {
  private readonly http = inject(HttpClient);

  create(
    contestId: number,
    index: string,
    language: string,
    code: string,
  ): Observable<Submission> {
    return this.http.post<Submission>(
      `/api/problems/${contestId}/${encodeURIComponent(index)}/submissions`,
      { language, code },
    );
  }

  list(limit = 20, offset = 0): Observable<SubmissionPage> {
    return this.http.get<SubmissionPage>('/api/users/me/submissions', {
      params: { limit, offset },
    });
  }

  get(id: number): Observable<SubmissionDetail> {
    return this.http.get<SubmissionDetail>(`/api/users/me/submissions/${id}`);
  }
}
