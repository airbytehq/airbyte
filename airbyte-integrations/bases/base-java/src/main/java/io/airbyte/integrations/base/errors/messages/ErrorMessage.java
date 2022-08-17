/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import io.airbyte.integrations.base.errors.utils.ConnectionErrorType;
import io.airbyte.integrations.base.errors.utils.ConnectorName;
import java.util.HashMap;
import java.util.Map;

public abstract class ErrorMessage {

  private static final String DEFAULT_ERROR_MESSAGE = "Standard error code: %s. \n Error Message: %s.";
  protected final Map<String, ConnectionErrorType> ERRORCODES_TYPES = new HashMap<>();

  public abstract ConnectorName getConnectorName();

  public String getDefaultErrorMessage(String errorCode, Exception exception) {
    return String.format(DEFAULT_ERROR_MESSAGE, errorCode, exception.getMessage());
  }

  public String getErrorMessage(String errorCode, Exception exception) {
    if (ERRORCODES_TYPES.containsKey(errorCode)) {
      return ERRORCODES_TYPES.get(errorCode).getValue();
    }
    return getDefaultErrorMessage(errorCode, exception);
  }

}
