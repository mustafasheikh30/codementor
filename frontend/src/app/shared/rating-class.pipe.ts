import { Pipe, PipeTransform } from '@angular/core';

// Codeforces colour tiers: newbie (gray) up to grandmaster (red).
const TIERS: [limit: number, cssClass: string][] = [
  [1200, 'r-gray'],
  [1400, 'r-green'],
  [1600, 'r-cyan'],
  [1900, 'r-blue'],
  [2100, 'r-violet'],
  [2400, 'r-orange'],
];

@Pipe({ name: 'ratingClass' })
export class RatingClassPipe implements PipeTransform {
  transform(rating: number | null): string {
    if (rating === null) return 'r-none';
    return TIERS.find(([limit]) => rating < limit)?.[1] ?? 'r-red';
  }
}
