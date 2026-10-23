import { Injectable, inject, signal } from '@angular/core';
import { catchError, of, tap } from 'rxjs';

import { AuthApi } from '../api/auth-api';
import { User } from '../api/models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly api = inject(AuthApi);

  readonly user = signal<User | null>(null);
  readonly loaded = signal(false);
  readonly loading = signal(false);

  load(): void {
    if (this.loading() || this.loaded()) return;
    this.loading.set(true);
    this.api
      .me()
      .pipe(
        tap((u) => {
          this.user.set(u);
          this.loaded.set(true);
          this.loading.set(false);
        }),
        catchError(() => {
          this.user.set(null);
          this.loaded.set(true);
          this.loading.set(false);
          return of(null);
        }),
      )
      .subscribe();
  }

  login(returnTo: string = '/problemset'): void {
    this.api.login(returnTo);
  }

  clear(): void {
    this.user.set(null);
    this.loaded.set(true);
    this.loading.set(false);
  }

  logout(): void {
    this.api.logout().subscribe({
      next: () => {
        this.user.set(null);
        this.loaded.set(true);
      },
      error: () => {
        this.user.set(null);
        this.loaded.set(true);
      },
    });
  }
}
