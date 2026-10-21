import { HttpErrorResponse } from '@angular/common/http';
import { Observable, catchError, map, of, startWith } from 'rxjs';

/** What a page shows while fetching: spinner text, an error, or the data. */
export type LoadState<T> =
  | { status: 'loading' }
  | { status: 'error'; notFound: boolean }
  | { status: 'ready'; data: T };

export const LOADING = { status: 'loading' } as const;

/** Wrap a request so it emits loading -> ready (or error) instead of throwing. */
export function load<T>(source: Observable<T>): Observable<LoadState<T>> {
  return source.pipe(
    map((data): LoadState<T> => ({ status: 'ready', data })),
    catchError((err: unknown) =>
      of<LoadState<T>>({
        status: 'error',
        notFound: err instanceof HttpErrorResponse && err.status === 404,
      }),
    ),
    startWith<LoadState<T>>(LOADING),
  );
}
