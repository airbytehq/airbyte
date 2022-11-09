// Take in any, because that is what JSON.stringify() takes in
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function formatJson(json: any): string {
  return JSON.stringify(json, null, 2);
}
