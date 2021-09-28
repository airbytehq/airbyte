/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.validation.json;

public class JsonValidationException extends Exception {

  public JsonValidationException(String message) {
    super(message);
  }

  public JsonValidationException(String message, Throwable cause) {
    super(message, cause);
  }

}
