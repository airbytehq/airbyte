/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.exception;

public class UnreachableWorkflowException extends Exception {

  public UnreachableWorkflowException(final String message) {
    super(message);
  }

  public UnreachableWorkflowException(final String message, final Throwable t) {
    super(message, t);
  }

}
