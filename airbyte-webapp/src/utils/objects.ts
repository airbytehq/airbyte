export function equal(
  o1?: Record<string, unknown> | Array<unknown> | null,
  o2?: Record<string, unknown> | Array<unknown> | null
): boolean {
  return JSON.stringify(o1) === JSON.stringify(o2);
}

export function naturalComparator(a: string, b: string): number {
  return a.localeCompare(b, undefined, { numeric: true });
}

export function naturalComparatorBy<T>(
  keyF: (obj: T) => string
): (a: T, b: T) => number {
  return (a, b) => naturalComparator(keyF(a), keyF(b));
}
