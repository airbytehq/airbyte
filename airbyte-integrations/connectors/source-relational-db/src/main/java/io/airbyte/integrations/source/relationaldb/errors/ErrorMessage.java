package io.airbyte.integrations.source.relationaldb.errors;

public interface ErrorMessage {

    String getErrorMessage(String stateCode, Exception exception);

    String getConnectorType();

    default String getDefaultErrorMessage(String stateCode, Exception exception) {
        StringBuilder sb = new StringBuilder("some standard message stateCode - ").append(stateCode)
                .append(" and error - ").append(exception.getMessage());
        return sb.toString();
    }
}
