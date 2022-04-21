package io.airbyte.workers;

public class RecordSchemaValidationException extends Exception {
  public RecordSchemaValidationException(final String message) {
    super(message);
  }
  public RecordSchemaValidationException(final String message, final Throwable cause) {
    super(message, cause);
  }
}
