export function isDefined<T>(a: T | null | undefined): a is Exclude<T, null | undefined> {
  return a !== undefined && a !== null;
}
