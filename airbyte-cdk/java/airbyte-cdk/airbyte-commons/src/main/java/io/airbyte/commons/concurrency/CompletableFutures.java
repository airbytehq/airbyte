/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import java.util.List;
import java.util.concurrent.CompletableFuture;

public class CompletableFutures {

  /**
   * Utility method which blocks until all futures are complete. Returns a list of the results of all
   * futures.
   *
   * @param futures
   * @return
   * @param <T>
   */
  public static <T> List<T> allOf(final List<CompletableFuture<T>> futures) {
    // return CompletableFuture
    // .allOf(futures.toArray(new CompletableFuture[0]))
    // .thenApply(v -> futures.stream().map(CompletableFuture::join).toList())
    // .join();
    return null;
  }

}
