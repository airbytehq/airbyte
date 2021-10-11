/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

public class ValueConflictKnownException extends KnownException {

  public ValueConflictKnownException(String message) {
    super(message);
  }

  public ValueConflictKnownException(String message, Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 409;
  }

}
