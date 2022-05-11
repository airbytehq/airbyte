/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_HOST;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.SNOWFLAKE;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class SnowflakeErrorMessage extends ErrorMessage {

  {
    CONSTANTS.put("08001", INCORRECT_USERNAME_OR_PASSWORD);
    CONSTANTS.put("28000", INCORRECT_USERNAME_OR_HOST);
  }

  @Override
  public ConnectorType getConnectorType() {
    return SNOWFLAKE;
  }

}
