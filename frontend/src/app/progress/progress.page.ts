import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

import { AuthApi } from '../api/auth-api';
import { SolvedEntry, User, UserProgress } from '../api/models';
import { AuthService } from '../auth/auth.service';

interface ProgressView {
  user: User | null;
  progress: UserProgress | null;
  solvedProblems: SolvedEntry[];
}

@Component({
  selector: 'app-progress',
  imports: [RouterLink],
  templateUrl: './progress.page.html',
  styleUrl: './progress.page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProgressPage {
  private readonly auth = inject(AuthService);
  private readonly authApi = inject(AuthApi);

  protected readonly data = toSignal(
    forkJoin({
      user: this.authApi.me().pipe(catchError(() => of(null as User | null))),
      progress: this.authApi.progress().pipe(catchError(() => of(null as UserProgress | null))),
      solved: this.authApi
        .solvedList()
        .pipe(catchError(() => of([] as SolvedEntry[]))),
    }).pipe(
      map(
        ({ user, progress, solved }): ProgressView => ({
          user,
          progress,
          solvedProblems: solved.slice(0, 100),
        }),
      ),
    ),
    { initialValue: null },
  );

  login(): void {
    this.auth.login('/progress');
  }
}
