package io.airbyte.cdk.integrations.base.operation;

public class OperationExecutionException extends Exception {
    public OperationExecutionException(final String message, final Throwable cause) {
        super(message, cause);
    }
}
