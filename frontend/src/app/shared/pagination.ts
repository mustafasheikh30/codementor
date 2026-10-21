/** One slot in the pager: a page number, or `null` for an ellipsis. */
export interface PageItem {
  n: number | null;
  current: boolean;
}

/** Builds items like: 1 … 4 [5] 6 … 20 */
export function pageItems(current: number, last: number): PageItem[] {
  const wanted = new Set<number>([1, last]);
  for (let n = Math.max(1, current - 2); n <= Math.min(last, current + 2); n++) wanted.add(n);

  const items: PageItem[] = [];
  let previous = 0;
  for (const n of [...wanted].sort((a, b) => a - b)) {
    if (n - previous > 1) items.push({ n: null, current: false });
    items.push({ n, current: n === current });
    previous = n;
  }
  return items;
}
