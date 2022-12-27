/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb.exception;

/**
 * Selectdb runtime exception.
 */
public class SelectdbRuntimeException extends RuntimeException {

  public SelectdbRuntimeException() {
    super();
  }

  public SelectdbRuntimeException(String message) {
    super(message);
  }

  public SelectdbRuntimeException(String message, Throwable cause) {
    super(message, cause);
  }

  public SelectdbRuntimeException(Throwable cause) {
    super(cause);
  }

  protected SelectdbRuntimeException(String message,
                                     Throwable cause,
                                     boolean enableSuppression,
                                     boolean writableStackTrace) {
    super(message, cause, enableSuppression, writableStackTrace);
  }

}
