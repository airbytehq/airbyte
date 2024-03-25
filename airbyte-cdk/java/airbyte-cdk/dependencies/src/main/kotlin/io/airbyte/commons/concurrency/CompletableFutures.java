/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import io.airbyte.commons.functional.Either;
import java.lang.reflect.Array;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.atomic.AtomicInteger;

public class CompletableFutures {

  /**
   * Non-blocking implementation which does not use join. and returns an aggregated future. The order
   * of results is preserved from the original list of futures.
   *
   * @param futures list of futures
   * @param <Result> type of result
   * @return a future that completes when all the input futures have completed
   */
  public static <Result> CompletionStage<List<Either<? extends Exception, Result>>> allOf(final List<CompletionStage<Result>> futures) {
    CompletableFuture<List<Either<? extends Exception, Result>>> result = new CompletableFuture<>();
    final int size = futures.size();
    final AtomicInteger counter = new AtomicInteger();
    @SuppressWarnings("unchecked")
    final Either<? extends Exception, Result>[] results = (Either<? extends Exception, Result>[]) Array.newInstance(Either.class, size);
    // attach a whenComplete to all futures
    for (int i = 0; i < size; i++) {
      final int currentIndex = i;
      futures.get(i).whenComplete((value, exception) -> {
        // if exception is null, then the future completed successfully
        // maybe synchronization is unnecessary here, but it's better to be safe
        synchronized (results) {
          if (exception == null) {
            results[currentIndex] = Either.right(value);
          } else {
            if (exception instanceof Exception) {
              results[currentIndex] = Either.left((Exception) exception);
            } else {
              // this should never happen
              throw new RuntimeException("Unexpected exception in a future completion.", exception);
            }
          }
        }
        int completedCount = counter.incrementAndGet();
        if (completedCount == size) {
          result.complete(Arrays.asList(results));
        }
      });
    }
    return result;
  }

}
