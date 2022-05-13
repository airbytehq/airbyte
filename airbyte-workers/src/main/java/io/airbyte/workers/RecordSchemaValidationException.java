/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

/**
 * Exception thrown by the RecordSchemaValidator during a sync when AirbyteRecordMessage data does
 * not conform to its stream's defined JSON schema
 */

public class RecordSchemaValidationException extends Exception {

  public RecordSchemaValidationException(final String message) {
    super(message);
  }

  public RecordSchemaValidationException(final String message, final Throwable cause) {
    super(message, cause);
  }

}
