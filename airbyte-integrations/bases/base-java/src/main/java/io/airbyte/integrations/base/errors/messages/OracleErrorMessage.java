/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_SCHEMA_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.ORACLE;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class OracleErrorMessage extends ErrorMessage {

  {
    CONSTANTS.put("72000", INCORRECT_USERNAME_OR_PASSWORD);
    CONSTANTS.put("08006", INCORRECT_HOST_OR_PORT);
  }

  @Override
  public ConnectorType getConnectorType() {
    return ORACLE;
  }

}
