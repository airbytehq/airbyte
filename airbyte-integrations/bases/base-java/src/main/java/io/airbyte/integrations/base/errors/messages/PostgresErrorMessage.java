/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectorType.POSTGRES;
import static io.airbyte.integrations.base.errors.utils.CustomExceptionUtils.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.CustomExceptionUtils.INCORRECT_USERNAME_OR_PASSWORD;

import io.airbyte.integrations.base.errors.utils.ConnectorType;
import java.util.HashMap;
import java.util.Map;

public class PostgresErrorMessage implements ErrorMessage {

  private final static Map<String, String> CONSTANTS = new HashMap<>();

  static {
    CONSTANTS.put("28P01", INCORRECT_USERNAME_OR_PASSWORD);
    CONSTANTS.put("08001", INCORRECT_HOST_OR_PORT);
  }

  @Override
  public String getErrorMessage(String stateCode, Exception exception) {
    if (CONSTANTS.containsKey(stateCode)) {
      return CONSTANTS.get(stateCode);
    }
    return getDefaultErrorMessage(stateCode, exception);
  }

  @Override
  public ConnectorType getConnectorType() {
    return POSTGRES;
  }

}
