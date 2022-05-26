/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import io.airbyte.integrations.base.errors.utils.ConnectionErrorType;
import io.airbyte.integrations.base.errors.utils.ConnectorType;
import java.util.HashMap;
import java.util.Map;

public abstract class ErrorMessage {

  private static final String DEFAULT_ERROR_MESSAGE = "Standard error code: %s. \n Error Message: %s.";
  protected final Map<String, ConnectionErrorType> CONSTANTS = new HashMap<>();

  public abstract ConnectorType getConnectorType();

  public String getDefaultErrorMessage(String errorCode, Exception exception) {
    return String.format(DEFAULT_ERROR_MESSAGE, errorCode, exception.getMessage());
  }

  public String getErrorMessage(String errorCode, Exception exception) {
    if (CONSTANTS.containsKey(errorCode)) {
      return CONSTANTS.get(errorCode).getValue();
    }
    return getDefaultErrorMessage(errorCode, exception);
  }

}
