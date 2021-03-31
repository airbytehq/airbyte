export function equal(
  o1?: Record<string, unknown> | Array<unknown> | null,
  o2?: Record<string, unknown> | Array<unknown> | null
): boolean {
  return JSON.stringify(o1) === JSON.stringify(o2);
}
