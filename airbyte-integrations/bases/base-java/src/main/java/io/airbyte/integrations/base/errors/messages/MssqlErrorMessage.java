/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE_OR_USER_ACCESS_DENIED;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.MSSQL;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class MssqlErrorMessage extends ErrorMessage {

  {
    CONSTANTS.put("S0001", INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE_OR_USER_ACCESS_DENIED);
    CONSTANTS.put("08S01", INCORRECT_HOST_OR_PORT);
  }

  @Override
  public ConnectorType getConnectorType() {
    return MSSQL;
  }

}
