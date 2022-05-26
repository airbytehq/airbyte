/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import io.airbyte.integrations.base.errors.utils.ConnectionErrorType;
import io.airbyte.integrations.base.errors.utils.ConnectorType;
import java.util.HashMap;
import java.util.Map;

public abstract class ErrorMessage {

  protected final Map<String, ConnectionErrorType> CONSTANTS = new HashMap<>();

  public abstract ConnectorType getConnectorType();

  public String getDefaultErrorMessage(String stateCode, Exception exception) {
    return "some standard message stateCode - " + stateCode +
        " and error - " + exception.getMessage();
  }

  public String getErrorMessage(String stateCode, Exception exception) {
    if (CONSTANTS.containsKey(stateCode)) {
      return CONSTANTS.get(stateCode).getValue();
    }
    return getDefaultErrorMessage(stateCode, exception);
  }

}
