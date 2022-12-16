/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.doris.exception;

public class IllegalArgumentException extends DorisException {

  public IllegalArgumentException(String msg, Throwable cause) {
    super(msg, cause);
  }

  public IllegalArgumentException(String arg, String value) {
    super("argument '" + arg + "' is illegal, value is '" + value + "'.");
  }

}
