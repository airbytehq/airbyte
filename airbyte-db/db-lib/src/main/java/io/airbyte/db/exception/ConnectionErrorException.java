/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.exception;

public class ConnectionErrorException extends RuntimeException {

  private String stateCode;
  private int errorCode;
  private String exceptionMessage;

  public ConnectionErrorException(String errorMessage) {
    super(errorMessage);
  }

  public ConnectionErrorException(String stateCode, String errorMessage) {
    super(errorMessage);
    this.stateCode = stateCode;
  }

  public ConnectionErrorException(String stateCode, Throwable exception) {
    super(exception);
    this.stateCode = stateCode;
  }

  public ConnectionErrorException(String stateCode,
                                  int errorCode,
                                  String exceptionMessage,
                                  Throwable exception) {
    super(exception);
    this.stateCode = stateCode;
    this.errorCode = errorCode;
    this.exceptionMessage = exceptionMessage;
  }

  public String getStateCode() {
    return this.stateCode;
  }

  public int getErrorCode() {
    return errorCode;
  }

  public String getExceptionMessage() {
    return exceptionMessage;
  }
}
