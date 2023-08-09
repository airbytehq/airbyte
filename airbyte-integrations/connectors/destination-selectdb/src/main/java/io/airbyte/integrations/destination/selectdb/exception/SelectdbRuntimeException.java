/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb.exception;

/**
 * Selectdb runtime exception.
 */
public class SelectdbRuntimeException extends RuntimeException {

  public SelectdbRuntimeException(String message) {
    super(message);
  }

  public SelectdbRuntimeException(Throwable cause) {
    super(cause);
  }

}
