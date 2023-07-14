/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.exception;

public class TestHarnessException extends Exception {

  public TestHarnessException(final String message) {
    super(message);
  }

  public TestHarnessException(final String message, final Throwable cause) {
    super(message, cause);
  }

}
