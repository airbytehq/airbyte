/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.REDSHIFT;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class RedshiftErrorMessage implements ErrorMessage {

  static {
    CONSTANTS.put("28000", INCORRECT_USERNAME_OR_PASSWORD);
    CONSTANTS.put("HY000", INCORRECT_HOST_OR_PORT);
    CONSTANTS.put("3D000", INCORRECT_DB_NAME);
  }

  @Override
  public ConnectorType getConnectorType() {
    return REDSHIFT;
  }

}
