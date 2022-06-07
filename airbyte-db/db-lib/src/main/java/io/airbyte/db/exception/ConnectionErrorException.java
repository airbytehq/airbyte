/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.exception;

public class ConnectionErrorException extends RuntimeException {

  private String errorCode;

  public ConnectionErrorException(String errorMessage) {
    super(errorMessage);
  }

  public ConnectionErrorException(String errorCode, String errorMessage) {
    super(errorMessage);
    this.errorCode = errorCode;
  }

  public ConnectionErrorException(String errorCode, Throwable exception) {
    super(exception);
    this.errorCode = errorCode;
  }

  public String getErrorCode() {
    return this.errorCode;
  }

}
