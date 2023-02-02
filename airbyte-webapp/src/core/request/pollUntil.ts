import { concatMap, delay, from, last, lastValueFrom, raceWith, takeWhile, timer, NEVER } from "rxjs";

/**
 * Repeatedly calls `apiFn` every `interval` milliseconds, until either `conditionFn`
 * returns `true` or `options.maxTimeout` milliseconds have elapsed. Returns a Promise
 * which resolves to `false` if `options.maxTimout` is reached or the value of `apiFn`
 * which passes the condition otherwise. If no `options.maxTimeout` is specified, it will
 * continue polling indefinitely until a matching value is found, so let's try not to DDOS
 * ourselves.
 *
 * Known issues:
 * - the case where `apiFn` returns `false` and `conditionFn(false) === true` is impossible
 *   to distinguish from a timeout, so don't poll for a boolean without first wrapping it
 *   with something like `.then(bool => ({ hopefullyUsefulFieldName: bool }))`.
 */
export function pollUntil<ResponseType>(
  apiFn: () => Promise<ResponseType>,
  conditionFn: (res: ResponseType) => boolean,
  options: { interval: number; maxTimeout?: number }
): Promise<ResponseType | false> {
  const { interval, maxTimeout } = options;
  const poll$ = timer(0, interval).pipe(
    concatMap((_) => from(apiFn())), // combine all emitted values into a single stream
    takeWhile((result) => !conditionFn(result), true),
    last() // only emit the latest polled value
  );

  const timeout$ = maxTimeout ? from([false] as Array<false>).pipe(delay(maxTimeout)) : NEVER;

  return lastValueFrom(poll$.pipe(raceWith(timeout$)));
}
