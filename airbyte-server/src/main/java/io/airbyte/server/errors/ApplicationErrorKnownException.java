/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

public class ApplicationErrorKnownException extends KnownException {

  public ApplicationErrorKnownException(String message) {
    super(message);
  }

  public ApplicationErrorKnownException(String message, Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 422;
  }

}
