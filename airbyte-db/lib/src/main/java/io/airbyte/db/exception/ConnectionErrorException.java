/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.exception;

public class ConnectionErrorException extends RuntimeException {

  private String customErrorCode;

  public ConnectionErrorException(String errorMessage) {
    super(errorMessage);
  }

  public ConnectionErrorException(String errorCode, String errorMessage) {
    super(errorMessage);
    this.customErrorCode = errorCode;
  }

  public ConnectionErrorException(String errorCode, Throwable exception) {
    super(exception);
    this.customErrorCode = errorCode;
  }

  public String getCustomErrorCode() {
    return this.customErrorCode;
  }

}
