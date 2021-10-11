/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

public class InternalServerKnownException extends KnownException {

  public InternalServerKnownException(String message) {
    super(message);
  }

  public InternalServerKnownException(String message, Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 500;
  }

}
