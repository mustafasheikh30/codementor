import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';

import { AuthApi } from '../api/auth-api';
import { SubmissionPage, SolvedCount } from '../api/models';
import { AuthService } from '../auth/auth.service';
import { LOADING, LoadState, load } from '../shared/load-state';
import { SubmissionApi } from '../api/submission-api';

@Component({
  selector: 'app-profile',
  imports: [RouterLink],
  templateUrl: './profile.page.html',
  styleUrl: './profile.page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProfilePage {
  protected readonly auth = inject(AuthService);
  private readonly api = inject(AuthApi);
  private readonly submissionApi = inject(SubmissionApi);

  protected readonly countState = toSignal(
    load(this.api.solvedCount()).pipe(
      catchError(() => of({ status: 'ready', data: { count: 0 } } as LoadState<SolvedCount>)),
    ),
    { initialValue: LOADING as LoadState<SolvedCount> },
  );

  protected readonly submissionState = toSignal(
    load(this.submissionApi.list(5)).pipe(
      catchError(() =>
        of({ status: 'ready', data: { total: 0, items: [] } } as LoadState<SubmissionPage>),
      ),
    ),
    { initialValue: LOADING as LoadState<SubmissionPage> },
  );

  login(): void {
    this.auth.login('/profile');
  }
}
