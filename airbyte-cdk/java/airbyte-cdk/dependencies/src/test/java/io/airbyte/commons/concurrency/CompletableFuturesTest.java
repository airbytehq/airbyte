/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.functional.Either;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import org.junit.jupiter.api.Test;

class CompletableFuturesTest {

  @Test
  public void testAllOf() {
    // Complete in random order
    final List<CompletionStage<Integer>> futures = Arrays.asList(
        returnSuccessWithDelay(1, 2000),
        returnSuccessWithDelay(2, 200),
        returnSuccessWithDelay(3, 500),
        returnSuccessWithDelay(4, 100),
        returnFailureWithDelay("Fail 5", 2000),
        returnFailureWithDelay("Fail 6", 300));

    final CompletableFuture<List<Either<? extends Exception, Integer>>> allOfResult = CompletableFutures.allOf(futures).toCompletableFuture();
    final List<Either<? extends Exception, Integer>> result = allOfResult.join();
    List<Either<? extends Exception, Integer>> success = result.stream().filter(Either::isRight).toList();
    assertEquals(success, Arrays.asList(
        Either.right(1),
        Either.right(2),
        Either.right(3),
        Either.right(4)));
    // Extract wrapped CompletionException messages.
    final List<String> failureMessages = result.stream().filter(Either::isLeft).map(either -> either.getLeft().getCause().getMessage()).toList();
    assertEquals(failureMessages, Arrays.asList("Fail 5", "Fail 6"));
  }

  private CompletableFuture<Integer> returnSuccessWithDelay(final int value, final long delayMs) {
    return CompletableFuture.supplyAsync(() -> {
      try {
        Thread.sleep(delayMs);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
      return value;
    });
  }

  private CompletableFuture<Integer> returnFailureWithDelay(final String message, final long delayMs) {
    return CompletableFuture.supplyAsync(() -> {
      try {
        Thread.sleep(delayMs);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
      throw new RuntimeException(message);
    });
  }

}
