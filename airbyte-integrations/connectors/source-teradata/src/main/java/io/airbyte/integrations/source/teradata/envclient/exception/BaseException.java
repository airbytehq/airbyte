/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata.envclient.exception;

public class BaseException extends RuntimeException {

  private final int statusCode;

  private final String body;

  private final String reason;

  public BaseException(int statusCode, String body) {
    super(body);
    this.statusCode = statusCode;
    this.body = body;
    this.reason = null;
  }

  public BaseException(int statusCode, String body, String reason) {
    super(body);
    this.statusCode = statusCode;
    this.body = body;
    this.reason = reason;
  }

  public int getStatusCode() {
    return statusCode;
  }

  public String getBody() {
    return body;
  }

  public String getReason() {
    return reason;
  }

}
