/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME_OR_USER_ACCESS_DENIED;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.MYSQL;

import io.airbyte.integrations.base.errors.utils.ConnectorName;

public class MysqlErrorMessage extends ErrorMessage {

  {
    ERRORCODES_TYPES.put("28000", INCORRECT_USERNAME_OR_PASSWORD);
    ERRORCODES_TYPES.put("08S01", INCORRECT_HOST_OR_PORT);
    ERRORCODES_TYPES.put("42000", INCORRECT_DB_NAME_OR_USER_ACCESS_DENIED);
  }

  @Override
  public ConnectorName getConnectorName() {
    return MYSQL;
  }

}
