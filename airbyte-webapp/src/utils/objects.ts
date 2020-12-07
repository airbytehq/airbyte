export function equal(
  o1?: Record<string, unknown> | null,
  o2?: Record<string, unknown> | null
): boolean {
  return JSON.stringify(o1) === JSON.stringify(o2);
}
