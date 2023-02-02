import { timer, delay, from, concatMap, takeWhile, last, raceWith, lastValueFrom, NEVER } from "rxjs";

// Known issues:
// - the case where `apiFn` returns `false` and `condition(false) === true` is impossible to distinguish from a timeout
export function pollUntil<ResponseType>(
  apiFn: () => Promise<ResponseType>,
  condition: (res: ResponseType) => boolean,
  interval: number,
  maxTimeout?: number
) {
  const poll$ = timer(0, interval).pipe(
    concatMap((_) => from(apiFn())),
    takeWhile((result) => !condition(result), true),
    last()
  );

  const timeout$ = maxTimeout ? from([false]).pipe(delay(maxTimeout)) : NEVER;

  return lastValueFrom(poll$.pipe(raceWith(timeout$)));
}
