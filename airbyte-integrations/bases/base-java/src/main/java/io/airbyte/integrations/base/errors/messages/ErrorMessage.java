package io.airbyte.integrations.base.errors.messages;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public interface ErrorMessage {

    String getErrorMessage(String stateCode, Exception exception);

    ConnectorType getConnectorType();

    default String getDefaultErrorMessage(String stateCode, Exception exception) {
        return "some standard message stateCode - " + stateCode +
                " and error - " + exception.getMessage();
    }
}
