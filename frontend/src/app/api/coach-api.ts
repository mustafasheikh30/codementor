import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { HintResponse } from './models';

@Injectable({ providedIn: 'root' })
export class CoachApi {
  private readonly http = inject(HttpClient);

  hint(contestId: number, index: string, code: string, level: number): Observable<HintResponse> {
    return this.http.post<HintResponse>(
      `/api/coach/hint?contest_id=${contestId}&index=${encodeURIComponent(index)}`,
      { code, level },
    );
  }
}
