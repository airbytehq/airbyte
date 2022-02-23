/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

public class BadObjectSchemaKnownException extends KnownException {

  public BadObjectSchemaKnownException(final String message) {
    super(message);
  }

  public BadObjectSchemaKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 422;
  }

}
