/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.exception;

public class ConnectionFileServiceErrorException extends RuntimeException {

  private final String customErrorCode;

  public ConnectionFileServiceErrorException(String errorCode, String errorMessage) {
    super(errorMessage);
    this.customErrorCode = errorCode;
  }

  public String getCustomErrorCode() {
    return this.customErrorCode;
  }

}
