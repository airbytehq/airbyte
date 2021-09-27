/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

public class ConnectFailureKnownException extends KnownException {

  public ConnectFailureKnownException(String message) {
    super(message);
  }

  public ConnectFailureKnownException(String message, Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 400;
  }

}
