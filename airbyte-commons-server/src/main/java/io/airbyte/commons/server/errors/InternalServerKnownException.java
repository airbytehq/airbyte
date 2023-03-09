/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

public class InternalServerKnownException extends KnownException {

  public InternalServerKnownException(final String message) {
    super(message);
  }

  public InternalServerKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 500;
  }

}
