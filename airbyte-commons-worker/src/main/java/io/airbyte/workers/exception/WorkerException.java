/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.exception;

public class WorkerException extends Exception {

  public WorkerException(final String message) {
    super(message);
  }

  public WorkerException(final String message, final Throwable cause) {
    super(message, cause);
  }

}
