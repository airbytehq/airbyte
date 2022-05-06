/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.exception;

public class ConnectionErrorException extends RuntimeException {

  private final String customErrorCode;

  public ConnectionErrorException(String errorCode, String errorMessage) {
    super(errorMessage);
    this.customErrorCode = errorCode;
  }

  public String getCustomErrorCode() {
    return this.customErrorCode;
  }

}
