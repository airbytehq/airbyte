package io.airbyte.workers.temporal.exception;

public class DeletedWorkflowException extends Exception {
  public DeletedWorkflowException(final String message) {
    super(message);
  }
}
