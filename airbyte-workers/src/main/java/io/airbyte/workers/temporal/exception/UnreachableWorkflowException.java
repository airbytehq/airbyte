/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.exception;

public class UnreachableWorkflowException extends Exception {

  public UnreachableWorkflowException(final String message, final Throwable t) {
    super(message, t);
  }

}
