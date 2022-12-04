import isEqual from "lodash/isEqual";

export function equal(o1?: unknown, o2?: unknown): boolean {
  return isEqual(o1, o2);
}

export function naturalComparator(a: string, b: string): number {
  return a.localeCompare(b, undefined, { numeric: true });
}

export function naturalComparatorBy<T>(keyF: (obj: T) => string): (a: T, b: T) => number {
  return (a, b) => naturalComparator(keyF(a), keyF(b));
}
