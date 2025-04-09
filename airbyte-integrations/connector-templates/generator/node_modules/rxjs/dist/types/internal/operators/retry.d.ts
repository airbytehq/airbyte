import { MonoTypeOperatorFunction, ObservableInput } from '../types';
export interface RetryConfig {
    /**
     * The maximum number of times to retry.
     */
    count?: number;
    /**
     * The number of milliseconds to delay before retrying, OR a function to
     * return a notifier for delaying. If a function is given, that function should
     * return a notifier that, when it emits will retry the source. If the notifier
     * completes _without_ emitting, the resulting observable will complete without error,
     * if the notifier errors, the error will be pushed to the result.
     */
    delay?: number | ((error: any, retryCount: number) => ObservableInput<any>);
    /**
     * Whether or not to reset the retry counter when the retried subscription
     * emits its first value.
     */
    resetOnSuccess?: boolean;
}
/**
 * Returns an Observable that mirrors the source Observable with the exception of an `error`. If the source Observable
 * calls `error`, this method will resubscribe to the source Observable for a maximum of `count` resubscriptions (given
 * as a number parameter) rather than propagating the `error` call.
 *
 * ![](retry.png)
 *
 * Any and all items emitted by the source Observable will be emitted by the resulting Observable, even those emitted
 * during failed subscriptions. For example, if an Observable fails at first but emits `[1, 2]` then succeeds the second
 * time and emits: `[1, 2, 3, 4, 5]` then the complete stream of emissions and notifications
 * would be: `[1, 2, 1, 2, 3, 4, 5, complete]`.
 *
 * ## Example
 *
 * ```ts
 * import { interval, mergeMap, throwError, of, retry } from 'rxjs';
 *
 * const source = interval(1000);
 * const result = source.pipe(
 *   mergeMap(val => val > 5 ? throwError(() => 'Error!') : of(val)),
 *   retry(2) // retry 2 times on error
 * );
 *
 * result.subscribe({
 *   next: value => console.log(value),
 *   error: err => console.log(`${ err }: Retried 2 times then quit!`)
 * });
 *
 * // Output:
 * // 0..1..2..3..4..5..
 * // 0..1..2..3..4..5..
 * // 0..1..2..3..4..5..
 * // 'Error!: Retried 2 times then quit!'
 * ```
 *
 * @see {@link retryWhen}
 *
 * @param count - Number of retry attempts before failing.
 * @param resetOnSuccess - When set to `true` every successful emission will reset the error count
 * @return A function that returns an Observable that will resubscribe to the
 * source stream when the source stream errors, at most `count` times.
 */
export declare function retry<T>(count?: number): MonoTypeOperatorFunction<T>;
/**
 * Returns an observable that mirrors the source observable unless it errors. If it errors, the source observable
 * will be resubscribed to (or "retried") based on the configuration passed here. See documentation
 * for {@link RetryConfig} for more details.
 *
 * @param config - The retry configuration
 */
export declare function retry<T>(config: RetryConfig): MonoTypeOperatorFunction<T>;
//# sourceMappingURL=retry.d.ts.map