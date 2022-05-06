/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_SCHEMA_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.ORACLE;

public class OracleErrorMessage implements ErrorMessage{
    static {
        CONSTANTS.put("72000", INCORRECT_USERNAME_OR_PASSWORD);
        CONSTANTS.put("08006", INCORRECT_HOST_OR_PORT);
        CONSTANTS.put("3D000", INCORRECT_SCHEMA_NAME);
    }

  @Override
  public ConnectorType getConnectorType() {
    return ORACLE;
  }

}
