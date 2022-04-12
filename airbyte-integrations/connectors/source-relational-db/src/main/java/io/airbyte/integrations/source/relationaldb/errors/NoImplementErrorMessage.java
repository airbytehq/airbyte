package io.airbyte.integrations.source.relationaldb.errors;

import io.airbyte.db.exception.CustomExceptionUtils;

public enum NoImplementErrorMessage implements ErrorMessage {

    NO_IMPLEMENTED_YET(CustomExceptionUtils.NO_IMPLEMENTED_YET, CustomExceptionUtils.NO_IMPLEMENTED_YET);

    final String stateCode;
    final String message;

    NoImplementErrorMessage(final String stateCode, final String message) {
        this.stateCode = stateCode;
        this.message = message;
    }

    @Override
    public String getErrorMessage(String stateCode, Exception exception) {
        return getDefaultErrorMessage(stateCode, exception);
    }

    @Override
    public String getConnectorType() {
        return CustomExceptionUtils.NO_IMPLEMENTED_YET;
    }

}
