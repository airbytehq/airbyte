package io.airbyte.integrations.source.relationaldb.errors;

import java.util.HashMap;
import java.util.Map;

import static io.airbyte.db.exception.CustomExceptionUtils.INCORRECT_HOST_OR_PORT;
import static io.airbyte.db.exception.CustomExceptionUtils.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.db.exception.CustomExceptionUtils.MY_SQL_CONNECTOR;

public enum MySQLErrorMessage implements ErrorMessage {

    AUTH_ERROR("28000", INCORRECT_USERNAME_OR_PASSWORD),
    HOST_OR_PORT_ERROR("08S01", INCORRECT_HOST_OR_PORT);

    final String stateCode;
    final String message;
    private final static Map<String, MySQLErrorMessage> CONSTANTS = new HashMap<>();

    static {
        for (MySQLErrorMessage c: values()) {
            CONSTANTS.put(c.stateCode, c);
        }
    }

    MySQLErrorMessage(final String stateCode, final String message) {
        this.stateCode = stateCode;
        this.message = message;
    }

    public String getMessage() {
        return this.message;
    }

    @Override
    public String getErrorMessage(String stateCode, Exception exception) {
        if (CONSTANTS.containsKey(stateCode)) {
            return CONSTANTS.get(stateCode).getMessage();
        }
        return getDefaultErrorMessage(stateCode, exception);
    }

    @Override
    public String getConnectorType() {
        return MY_SQL_CONNECTOR;
    }

}
