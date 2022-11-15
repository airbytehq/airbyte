/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.exception;

public class DorisException extends Exception {

  public DorisException() {
    super();
  }

  public DorisException(String message) {
    super(message);
  }

  public DorisException(String message, Throwable cause) {
    super(message, cause);
  }

  public DorisException(Throwable cause) {
    super(cause);
  }

  protected DorisException(String message,
                           Throwable cause,
                           boolean enableSuppression,
                           boolean writableStackTrace) {
    super(message, cause, enableSuppression, writableStackTrace);
  }

}
