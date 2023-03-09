/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

public class ApplicationErrorKnownException extends KnownException {

  public ApplicationErrorKnownException(final String message) {
    super(message);
  }

  public ApplicationErrorKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 422;
  }

}
