package io.airbyte.integrations.source.elasticsearch;

public class UnsupportedDatatypeException extends Exception {
    public UnsupportedDatatypeException(String message) {
        super(message);
    }
}
