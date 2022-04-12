package io.airbyte.integrations.source.relationaldb.errors;

import java.util.HashMap;
import java.util.Map;

import static io.airbyte.db.exception.CustomExceptionUtils.INCORRECT_HOST_OR_PORT;
import static io.airbyte.db.exception.CustomExceptionUtils.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.db.exception.CustomExceptionUtils.MS_SQL_CONNECTOR;

public enum MsSQLErrorMessage implements ErrorMessage {

    AUTH_ERROR("S0001", INCORRECT_USERNAME_OR_PASSWORD),
    HOST_OR_PORT_ERROR("08S01", INCORRECT_HOST_OR_PORT);

    final String stateCode;
    final String message;
    private final static Map<String, MsSQLErrorMessage> CONSTANTS = new HashMap<>();

    static {
        for (MsSQLErrorMessage c: values()) {
            CONSTANTS.put(c.stateCode, c);
        }
    }

    MsSQLErrorMessage(final String stateCode, final String message) {
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
        return MS_SQL_CONNECTOR;
    }

}
