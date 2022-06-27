/**
 * Returns a promise that rejects after `delay` milliseconds with the given reason.
 */
export function rejectAfter(delay: number, reason: string) {
  return new Promise((_, reject) => {
    window.setTimeout(() => reject(reason), delay);
  });
}
