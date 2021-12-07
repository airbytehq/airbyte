/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.exception;

public class NonRetryableException extends RuntimeException {

  public NonRetryableException(final Exception e) {
    super(e);
  }

}
