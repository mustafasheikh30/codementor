import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { switchMap } from 'rxjs';

import { Problem } from '../api/models';
import { ProblemApi } from '../api/problem-api';
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

  protected readonly state = toSignal(
    this.route.paramMap.pipe(
      switchMap((p) => load(this.api.get(p.get('contestId') ?? '', p.get('index') ?? ''))),
    ),
    { initialValue: LOADING as LoadState<Problem> },
  );
}
