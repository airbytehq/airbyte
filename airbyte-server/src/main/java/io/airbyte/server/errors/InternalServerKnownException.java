/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.micronaut.http.HttpStatus;

public class InternalServerKnownException extends KnownException {

  public InternalServerKnownException(final String message) {
    super(message);
  }

  public InternalServerKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return HttpStatus.INTERNAL_SERVER_ERROR.getCode();
  }

}
