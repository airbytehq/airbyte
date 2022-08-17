/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE_OR_USER_ACCESS_DENIED;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.MSSQL;

import io.airbyte.integrations.base.errors.utils.ConnectorName;

public class MssqlErrorMessage extends ErrorMessage {

  {
    ERRORCODES_TYPES.put("S0001", INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE_OR_USER_ACCESS_DENIED);
    ERRORCODES_TYPES.put("08S01", INCORRECT_HOST_OR_PORT);
  }

  @Override
  public ConnectorName getConnectorName() {
    return MSSQL;
  }

}
