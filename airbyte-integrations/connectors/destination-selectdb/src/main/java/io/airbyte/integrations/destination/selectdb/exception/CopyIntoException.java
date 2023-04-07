/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.selectdb.exception;

public class CopyIntoException extends SelectdbRuntimeException {

  public CopyIntoException(String message) {
    super(message);
  }

}
