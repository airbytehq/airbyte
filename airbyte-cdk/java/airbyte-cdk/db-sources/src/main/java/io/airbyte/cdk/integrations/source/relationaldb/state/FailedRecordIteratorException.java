package io.airbyte.cdk.integrations.source.relationaldb.state;

public class FailedRecordIteratorException extends RuntimeException {
  public FailedRecordIteratorException(Throwable cause) {
    super(cause);
  }

}
