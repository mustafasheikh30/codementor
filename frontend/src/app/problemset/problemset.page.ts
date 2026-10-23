import { ChangeDetectionStrategy, Component, computed, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, map, of, switchMap, tap } from 'rxjs';

import { ProblemApi } from '../api/problem-api';
import { AuthApi } from '../api/auth-api';
import { AuthService } from '../auth/auth.service';
import { Meta, ProblemPage, ProblemQuery, TagCount } from '../api/models';
import { LOADING, LoadState, load } from '../shared/load-state';
import { pageItems } from '../shared/pagination';
import { RatingClassPipe } from '../shared/rating-class.pipe';

@Component({
  selector: 'app-problemset',
  imports: [ReactiveFormsModule, RouterLink, RatingClassPipe],
  templateUrl: './problemset.page.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProblemsetPage {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly api = inject(ProblemApi);
  private readonly authApi = inject(AuthApi);
  protected readonly auth = inject(AuthService);

  protected readonly solvedSet = toSignal(
    this.authApi.solvedList().pipe(
      map((list) => new Set(list.map((s) => `${s.contest_id}${s.index}`))),
      catchError(() => of(new Set<string>())),
    ),
    { initialValue: new Set<string>() },
  );

  protected readonly form = new FormGroup({
    q: new FormControl('', { nonNullable: true }),
    tag: new FormControl('', { nonNullable: true }),
    min_rating: new FormControl('', { nonNullable: true }),
    max_rating: new FormControl('', { nonNullable: true }),
    sort: new FormControl('newest', { nonNullable: true }),
    solved: new FormControl('', { nonNullable: true }),
  });

  protected readonly tags = toSignal(
    this.api.tags().pipe(catchError(() => of<TagCount[]>([]))),
    { initialValue: [] as TagCount[] },
  );

  protected readonly meta = toSignal(
    this.api.meta().pipe(catchError(() => of<Meta | null>(null))),
    { initialValue: null as Meta | null },
  );

  // The URL is the single source of truth for filters, so every view is linkable and
  // the back button works. Changing the URL re-fetches and re-fills the form.
  protected readonly state = toSignal(
    this.route.queryParamMap.pipe(
      map(
        (p): ProblemQuery => ({
          q: p.get('q') ?? '',
          tag: p.get('tag') ?? '',
          min_rating: p.get('min_rating') ?? '',
          max_rating: p.get('max_rating') ?? '',
          sort: p.get('sort') ?? 'newest',
          solved: p.get('solved') ?? '',
          page: Number(p.get('page')) || 1,
        }),
      ),
      tap((query) => this.form.patchValue(query)),
      switchMap((query) => load(this.api.list(query))),
    ),
    { initialValue: LOADING as LoadState<ProblemPage> },
  );

  protected readonly pages = computed(() => {
    const s = this.state();
    if (s.status !== 'ready') return [];
    return pageItems(s.data.page, Math.max(1, Math.ceil(s.data.total / s.data.page_size)));
  });

  protected apply(): void {
    const v = this.form.getRawValue();
    // `null` drops a param from the URL, keeping links short.
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: {
        q: v.q.trim() || null,
        tag: v.tag || null,
        min_rating: v.min_rating || null,
        max_rating: v.max_rating || null,
        sort: v.sort === 'newest' ? null : v.sort,
        solved: v.solved || null,
        page: null,
      },
    });
  }
}
