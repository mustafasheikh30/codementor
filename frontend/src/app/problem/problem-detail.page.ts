import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, of, switchMap } from 'rxjs';

import { Problem } from '../api/models';
import { ProblemApi } from '../api/problem-api';
import { AuthApi } from '../api/auth-api';
import { CoachApi } from '../api/coach-api';
import { SubmissionApi } from '../api/submission-api';
import { AuthService } from '../auth/auth.service';
import { LOADING, LoadState, load } from '../shared/load-state';
import { RatingClassPipe } from '../shared/rating-class.pipe';

@Component({
  selector: 'app-problem-detail',
  imports: [RouterLink, RatingClassPipe],
  templateUrl: './problem-detail.page.html',
  styleUrl: './problem-detail.page.css',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProblemDetailPage {
  private readonly route = inject(ActivatedRoute);
  private readonly api = inject(ProblemApi);
  private readonly authApi = inject(AuthApi);
  private readonly coachApi = inject(CoachApi);
  private readonly submissionApi = inject(SubmissionApi);
  protected readonly auth = inject(AuthService);

  protected readonly state = toSignal(
    this.route.paramMap.pipe(
      switchMap((p) => load(this.api.get(p.get('contestId') ?? '', p.get('index') ?? ''))),
    ),
    { initialValue: LOADING as LoadState<Problem> },
  );

  protected readonly solved = signal(false);
  protected readonly code = signal('');
  protected readonly hint = signal<string | null>(null);
  protected readonly hintLevel = signal(0);
  protected readonly hintLoading = signal(false);
  protected readonly hintError = signal<string | null>(null);
  protected readonly language = signal('Python 3');
  protected readonly submissionMessage = signal<string | null>(null);
  protected readonly submissionError = signal<string | null>(null);
  protected readonly submissionLoading = signal(false);

  constructor() {
    this.route.paramMap
      .pipe(
        switchMap((p) => {
          this.hint.set(null);
          this.hintLevel.set(0);
          this.hintError.set(null);
          this.submissionMessage.set(null);
          this.submissionError.set(null);
          const c = Number(p.get('contestId'));
          const i = p.get('index') ?? '';
          return this.authApi.getSolvedStatus(c, i).pipe(catchError(() => of({ solved: false })));
        }),
      )
      .subscribe((s) => this.solved.set(s.solved));
  }

  toggleSolved(): void {
    const s = this.state();
    if (s.status !== 'ready' || !this.auth.user()) return;
    const c = s.data.contest_id;
    const i = s.data.index;
    const request$ = this.solved()
      ? this.authApi.unmarkSolved(c, i)
      : this.authApi.markSolved(c, i);
    request$.subscribe({
      next: (r) => this.solved.set(r.solved),
      // A 401 here means the session expired; let the header reflect that.
      error: () => this.auth.clear(),
    });
  }

  requestHint(): void {
    const s = this.state();
    if (s.status !== 'ready') return;
    if (!this.auth.user()) {
      this.login();
      return;
    }
    const code = this.code().trim();
    if (!code) {
      this.hintError.set('Paste your current solution first.');
      return;
    }
    const level = this.hint() ? Math.min(this.hintLevel() + 1, 3) : 1;
    this.hintLoading.set(true);
    this.hintError.set(null);
    this.coachApi.hint(s.data.contest_id, s.data.index, code, level).subscribe({
      next: (response) => {
        this.hint.set(response.hint);
        this.hintLevel.set(level);
        this.hintLoading.set(false);
      },
      error: (error: { status?: number }) => {
        this.hintLoading.set(false);
        if (error.status === 401) {
          this.auth.clear();
          this.hintError.set('Your session expired. Sign in again for hints.');
        } else if (error.status === 503) {
          this.hintError.set('The coach is not configured on this server.');
        } else {
          this.hintError.set('Could not get a hint. Try again.');
        }
      },
    });
  }

  recordSubmission(): void {
    const s = this.state();
    if (s.status !== 'ready') return;
    if (!this.auth.user()) {
      this.login();
      return;
    }
    const code = this.code().trim();
    if (!code) {
      this.submissionError.set('Paste your solution before recording it.');
      this.submissionMessage.set(null);
      return;
    }
    const language = this.language().trim();
    if (!language) {
      this.submissionError.set('Add a language before recording it.');
      this.submissionMessage.set(null);
      return;
    }
    this.submissionLoading.set(true);
    this.submissionError.set(null);
    this.submissionMessage.set(null);
    this.submissionApi.create(s.data.contest_id, s.data.index, language, this.code()).subscribe({
      next: (submission) => {
        this.submissionLoading.set(false);
        this.submissionMessage.set(
          `Recorded submission #${submission.id} (${submission.language}).`,
        );
      },
      error: (error: { status?: number }) => {
        this.submissionLoading.set(false);
        if (error.status === 401) {
          this.auth.clear();
          this.submissionError.set('Your session expired. Sign in again to record submissions.');
        } else if (error.status === 404) {
          this.submissionError.set('Problem not found.');
        } else {
          this.submissionError.set('Could not record the submission. Try again.');
        }
      },
    });
  }

  login(): void {
    const s = this.state();
    const returnTo = s.status === 'ready' ? `/problem/${s.data.contest_id}/${s.data.index}` : '/problemset';
    this.auth.login(returnTo);
  }
}
