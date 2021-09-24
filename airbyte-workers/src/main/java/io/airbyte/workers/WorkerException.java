/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

public class WorkerException extends Exception {

  public WorkerException(String message) {
    super(message);
  }

  public WorkerException(String message, Throwable cause) {
    super(message, cause);
  }

}
