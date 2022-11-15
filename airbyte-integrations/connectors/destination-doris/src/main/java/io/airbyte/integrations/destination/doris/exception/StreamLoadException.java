/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.exception;

public class StreamLoadException extends Exception {

  public StreamLoadException() {
    super();
  }

  public StreamLoadException(String message) {
    super(message);
  }

  public StreamLoadException(String message, Throwable cause) {
    super(message, cause);
  }

  public StreamLoadException(Throwable cause) {
    super(cause);
  }

  protected StreamLoadException(String message,
                                Throwable cause,
                                boolean enableSuppression,
                                boolean writableStackTrace) {
    super(message, cause, enableSuppression, writableStackTrace);
  }

}
