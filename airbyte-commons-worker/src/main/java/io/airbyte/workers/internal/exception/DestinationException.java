/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.exception;

public class DestinationException extends RuntimeException {

  public DestinationException(final String message) {
    super(message);
  }

  public DestinationException(final String message, final Throwable cause) {
    super(message, cause);
  }

}
