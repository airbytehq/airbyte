/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.micronaut.http.HttpStatus;

public class BadObjectSchemaKnownException extends KnownException {

  public BadObjectSchemaKnownException(final String message) {
    super(message);
  }

  public BadObjectSchemaKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return HttpStatus.UNPROCESSABLE_ENTITY.getCode();
  }

}
