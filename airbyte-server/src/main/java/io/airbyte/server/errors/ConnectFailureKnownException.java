/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

public class ConnectFailureKnownException extends KnownException {

  public ConnectFailureKnownException(final String message) {
    super(message);
  }

  public ConnectFailureKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 400;
  }

}
