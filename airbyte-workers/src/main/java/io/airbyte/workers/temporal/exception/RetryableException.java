/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.exception;

public class RetryableException extends RuntimeException {

  public RetryableException(final Exception e) {
    super(e);
  }

}
