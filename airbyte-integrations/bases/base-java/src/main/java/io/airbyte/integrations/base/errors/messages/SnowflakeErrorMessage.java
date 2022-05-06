/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import io.airbyte.integrations.base.errors.utils.ConnectorType;


import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_HOST;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.SNOWFLAKE;

public class SnowflakeErrorMessage implements ErrorMessage{
    static {
        CONSTANTS.put("08001", INCORRECT_PASSWORD);
        CONSTANTS.put("28000", INCORRECT_USERNAME_OR_HOST);
    }

  @Override
  public ConnectorType getConnectorType() {
    return SNOWFLAKE;
  }

}
