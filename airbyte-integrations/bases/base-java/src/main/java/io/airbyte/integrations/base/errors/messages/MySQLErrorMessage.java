/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.MYSQL;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class MySQLErrorMessage implements ErrorMessage {

  static {
    CONSTANTS.put("28000", INCORRECT_USERNAME_OR_PASSWORD);
    CONSTANTS.put("08S01", INCORRECT_HOST_OR_PORT);
    CONSTANTS.put("42000", INCORRECT_HOST_OR_PORT);
  }

  @Override
  public ConnectorType getConnectorType() {
    return MYSQL;
  }

}
