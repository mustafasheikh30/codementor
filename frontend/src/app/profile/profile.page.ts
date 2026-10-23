import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, of } from 'rxjs';

import { AuthApi } from '../api/auth-api';
import { SolvedCount } from '../api/models';
import { AuthService } from '../auth/auth.service';
import { LOADING, LoadState, load } from '../shared/load-state';

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

  protected readonly countState = toSignal(
    load(this.api.solvedCount()).pipe(
      catchError(() => of({ status: 'ready', data: { count: 0 } } as LoadState<SolvedCount>)),
    ),
    { initialValue: LOADING as LoadState<SolvedCount> },
  );

  login(): void {
    this.auth.login('/profile');
  }
}
