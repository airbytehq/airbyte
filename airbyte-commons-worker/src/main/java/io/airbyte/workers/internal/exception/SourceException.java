package io.airbyte.workers.internal.exception;

public class SourceException extends RuntimeException {

    public SourceException(final String message) {
        super(message);
    }

    public SourceException(final String message, final Throwable cause) {
        super(message, cause);
    }

}
