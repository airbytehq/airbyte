/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

public class ValueConflictKnownException extends KnownException {

  public ValueConflictKnownException(final String message) {
    super(message);
  }

  public ValueConflictKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 409;
  }

}
