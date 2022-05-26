/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME_OR_USER_ACCESS_DENIED;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.MYSQL;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class MysqlErrorMessage extends ErrorMessage {

  {
    CONSTANTS.put("28000", INCORRECT_USERNAME_OR_PASSWORD);
    CONSTANTS.put("08S01", INCORRECT_HOST_OR_PORT);
    CONSTANTS.put("42000", INCORRECT_DB_NAME_OR_USER_ACCESS_DENIED);
  }

  @Override
  public ConnectorType getConnectorType() {
    return MYSQL;
  }

}
