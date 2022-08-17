/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_HOST;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.SNOWFLAKE;

import io.airbyte.integrations.base.errors.utils.ConnectorName;

public class SnowflakeErrorMessage extends ErrorMessage {

  {
    ERRORCODES_TYPES.put("08001", INCORRECT_USERNAME_OR_PASSWORD);
    ERRORCODES_TYPES.put("28000", INCORRECT_USERNAME_OR_HOST);
  }

  @Override
  public ConnectorName getConnectorName() {
    return SNOWFLAKE;
  }

}
