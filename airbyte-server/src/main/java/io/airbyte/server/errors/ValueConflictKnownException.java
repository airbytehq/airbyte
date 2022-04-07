/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.micronaut.http.HttpStatus;

public class ValueConflictKnownException extends KnownException {

  public ValueConflictKnownException(final String message) {
    super(message);
  }

  public ValueConflictKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return HttpStatus.CONFLICT.getCode();
  }

}
