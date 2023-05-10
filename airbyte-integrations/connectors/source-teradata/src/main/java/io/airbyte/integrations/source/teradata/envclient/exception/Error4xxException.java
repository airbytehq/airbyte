/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata.envclient.exception;

public class Error4xxException extends BaseException {

  public Error4xxException(int statusCode, String body, String reason) {
    super(statusCode, body, reason);
  }

  public Error4xxException(int statusCode, String body) {
    super(statusCode, body);
  }

}
