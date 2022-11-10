// Take in any, because that is what JSON.stringify() takes in
export function formatJson(json: unknown): string {
  return JSON.stringify(json, null, 2);
}
