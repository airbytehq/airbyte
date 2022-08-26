/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.exception;

public class ConnectionErrorException extends RuntimeException {

  private String stateCode;
  private int errorCode;
  private String exceptionMessage;

  public ConnectionErrorException(String exceptionMessage) {
    super(exceptionMessage);
  }

  public ConnectionErrorException(String stateCode, Throwable exception) {
    super(exception);
    this.stateCode = stateCode;
    this.exceptionMessage = exception.getLocalizedMessage();
  }

  public ConnectionErrorException(String stateCode,
                                  String exceptionMessage,
                                  Throwable exception) {
    super(exception);
    this.stateCode = stateCode;
    this.exceptionMessage = exceptionMessage;
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
