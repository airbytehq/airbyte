/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.exception;

import java.util.Set;

/**
 * Exception thrown by the RecordSchemaValidator during a sync when AirbyteRecordMessage data does
 * not conform to its stream's defined JSON schema
 */

public class RecordSchemaValidationException extends Exception {

  public final Set<String> errorMessages;

  public RecordSchemaValidationException(final Set<String> errorMessages, final String message) {
    super(message);
    this.errorMessages = errorMessages;
  }

  public RecordSchemaValidationException(final Set<String> errorMessages, final String message, final Throwable cause) {
    super(message, cause);
    this.errorMessages = errorMessages;
  }

}
