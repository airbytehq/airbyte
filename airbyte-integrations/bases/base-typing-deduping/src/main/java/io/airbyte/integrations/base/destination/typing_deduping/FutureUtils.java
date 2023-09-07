/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import java.util.Collection;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;

public class FutureUtils {

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

  public static void reduceExceptions(final Collection<CompletableFuture<Optional<Exception>>> potentialExceptions, final String initialMessage)
      throws Exception {
    final var exceptionMessages = potentialExceptions.stream()
        .map(CompletableFuture::join)
        .filter(Optional::isPresent)
        .map(Optional::get)
        .map(Exception::getMessage)
        .collect(Collectors.joining("\n"));
    if (StringUtils.isNotBlank(exceptionMessages)) {
      throw new Exception(initialMessage + exceptionMessages);
    }
  }

}
