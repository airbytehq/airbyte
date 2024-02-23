/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

public class FutureUtils {

  private static final int DEFAULT_TD_THREAD_COUNT = 8;

  /**
   * Allow for configuring the number of typing and deduping threads via an environment variable in
   * the destination container.
   *
   * @return the number of threads to use in the typing and deduping pool
   */
  public static int getCountOfTypeAndDedupeThreads() {
    return Optional.ofNullable(System.getenv("TD_THREADS"))
        .map(Integer::valueOf)
        .orElse(DEFAULT_TD_THREAD_COUNT);
  }

  /**
   * Log all exceptions from a list of futures, and rethrow the first exception if there is one. This
   * mimics the behavior of running the futures in serial, where the first failure
   */
  public static void reduceExceptions(final Collection<CompletableFuture<Optional<Exception>>> potentialExceptions, final String initialMessage)
      throws Exception {
    final List<Exception> exceptions = potentialExceptions.stream()
        .map(CompletableFuture::join)
        .filter(Optional::isPresent)
        .map(Optional::get)
        .toList();
    ConnectorExceptionUtil.logAllAndThrowFirst(initialMessage, exceptions);
  }

}
