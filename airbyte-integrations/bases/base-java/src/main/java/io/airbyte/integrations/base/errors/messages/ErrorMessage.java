/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import io.airbyte.integrations.base.errors.utils.ConnectionErrorType;
import io.airbyte.integrations.base.errors.utils.ConnectorName;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

public abstract class ErrorMessage {

  private static final String DEFAULT_ERROR_MESSAGE = "State code: %s. \n Error Message: %s.";
  protected final Map<String, ConnectionErrorType> CONSTANTS = new HashMap<>();

  public abstract ConnectorName getConnectorName();

  public String getDefaultErrorMessage(String errorCode, Exception exception) {
    return String.format(DEFAULT_ERROR_MESSAGE, errorCode, exception.getMessage());
  }

  public String getErrorMessage(String stateCode, int errorCode, String message, Exception exception) {
    if (Objects.isNull(message)) {
      if (CONSTANTS.containsKey(stateCode)) {
        return CONSTANTS.get(stateCode).getValue();
      }
      return getDefaultErrorMessage(stateCode, exception);
    } else {
      return configMessage(stateCode, errorCode, message);
    }
  }

  private String configMessage(String stateCode, int errorCode, String message) {
    var stateCodePart = Objects.isNull(stateCode) ? "" : "State code: " + stateCode + "; ";
    var errorCodePart = errorCode == 0 ? "" : "Error code: " + errorCode + "; ";
    return stateCodePart + errorCodePart + "Message: " + message;
  }

}
