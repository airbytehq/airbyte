/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

public class BadObjectSchemaKnownException extends KnownException {

  public BadObjectSchemaKnownException(String message) {
    super(message);
  }

  public BadObjectSchemaKnownException(String message, Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 422;
  }

}
