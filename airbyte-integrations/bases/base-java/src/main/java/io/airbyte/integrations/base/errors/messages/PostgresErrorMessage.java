/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_ACCESS_PERMISSION;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.POSTGRES;

import io.airbyte.integrations.base.errors.utils.ConnectorName;

public class PostgresErrorMessage extends ErrorMessage {

  {
    ERRORCODES_TYPES.put("28P01", INCORRECT_USERNAME_OR_PASSWORD);
    ERRORCODES_TYPES.put("42501", INCORRECT_ACCESS_PERMISSION);
    ERRORCODES_TYPES.put("08001", INCORRECT_HOST_OR_PORT);
    ERRORCODES_TYPES.put("3D000", INCORRECT_DB_NAME);
  }

  @Override
  public ConnectorName getConnectorName() {
    return POSTGRES;
  }

}
