/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.exception;

public class CustomExceptionWrapper extends RuntimeException {

  private final String customErrorCode;

  public CustomExceptionWrapper(String errorCode, String errorMessage) {
    super(errorMessage);
    this.customErrorCode = errorCode;
  }

  public String getCustomErrorCode() {
    return this.customErrorCode;
  }

}
