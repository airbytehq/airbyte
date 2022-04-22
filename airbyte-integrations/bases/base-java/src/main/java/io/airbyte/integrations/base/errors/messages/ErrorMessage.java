/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import io.airbyte.integrations.base.errors.utils.ConnectionErrorType;
import io.airbyte.integrations.base.errors.utils.ConnectorType;
import java.util.HashMap;
import java.util.Map;

public interface ErrorMessage {

  Map<String, ConnectionErrorType> CONSTANTS = new HashMap<>();

  ConnectorType getConnectorType();

  default String getDefaultErrorMessage(String stateCode, Exception exception) {
    return "some standard message stateCode - " + stateCode +
        " and error - " + exception.getMessage();
  }

  default String getErrorMessage(String stateCode, Exception exception) {
    if (CONSTANTS.containsKey(stateCode)) {
      return CONSTANTS.get(stateCode).getValue();
    }
    return getDefaultErrorMessage(stateCode, exception);
  }

}
