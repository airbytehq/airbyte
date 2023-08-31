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

  public static void reduceExceptions(Collection<CompletableFuture<Optional<Exception>>> potentialExceptions, String initialMessage)
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
