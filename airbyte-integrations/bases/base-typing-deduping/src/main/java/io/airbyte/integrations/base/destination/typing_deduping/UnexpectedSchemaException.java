package io.airbyte.integrations.base.destination.typing_deduping;

public class UnexpectedSchemaException extends RuntimeException {

    public UnexpectedSchemaException(String message) {super(message); }

}
