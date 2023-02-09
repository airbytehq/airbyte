import { timer, delay, from, concatMap, takeWhile, last, raceWith, lastValueFrom, NEVER } from "rxjs";

// Known issues:
// - the case where `apiFn` returns `false` and `condition(false) === true` is impossible to distinguish from a timeout
export function pollUntil<ResponseType>(
  apiFn: () => Promise<ResponseType>,
  condition: (res: ResponseType) => boolean,
  options: { intervalMs: number; maxTimeoutMs?: number }
) {
  const { intervalMs, maxTimeoutMs } = options;
  const poll$ = timer(0, intervalMs).pipe(
    concatMap(() => from(apiFn())),
    takeWhile((result) => !condition(result), true),
    last()
  );

  const timeout$ = maxTimeoutMs ? from([false]).pipe(delay(maxTimeoutMs)) : NEVER;

  return lastValueFrom(poll$.pipe(raceWith(timeout$)));
}
