export function formatJson(json: unknown): string {
  return JSON.stringify(json, null, 2);
}
