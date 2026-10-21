import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-not-found',
  imports: [RouterLink],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <section class="roundbox">
      <div class="caption">Page not found</div>
      <div class="empty">
        That page doesn't exist. <a routerLink="/problemset">Back to the problemset</a>
      </div>
    </section>
  `,
})
export class NotFoundPage {}
