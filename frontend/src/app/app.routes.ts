import { Routes } from '@angular/router';

// Pages are lazy-loaded so the first download stays small as the app grows.
export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'problemset' },
  {
    path: 'problemset',
    title: 'Problemset · CodeMentor',
    loadComponent: () => import('./problemset/problemset.page').then((m) => m.ProblemsetPage),
  },
  {
    path: 'problem/:contestId/:index',
    title: 'Problem · CodeMentor',
    loadComponent: () => import('./problem/problem-detail.page').then((m) => m.ProblemDetailPage),
  },
  {
    path: '**',
    title: 'Not found · CodeMentor',
    loadComponent: () => import('./shared/not-found.page').then((m) => m.NotFoundPage),
  },
];
