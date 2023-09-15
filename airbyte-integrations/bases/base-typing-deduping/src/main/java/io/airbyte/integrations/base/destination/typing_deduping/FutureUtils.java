/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import static java.util.stream.Collectors.joining;

import io.airbyte.integrations.util.ConnectorExceptionUtil;
import java.util.Collection;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class FutureUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(FutureUtils.class);

  /**
   * Allow for configuring the number of typing and deduping threads via an enviornment variable in
   * the destination container.
   *
   * @return the number of threads to use in the typing and deduping pool
   */
  public static int countOfTypingDedupingThreads(final int defaultThreads) {
    return Optional.ofNullable(System.getenv("TD_THREADS"))
        .map(Integer::valueOf)
        .orElse(defaultThreads);
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
