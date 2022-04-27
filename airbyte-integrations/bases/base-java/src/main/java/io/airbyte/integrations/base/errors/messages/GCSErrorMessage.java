/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.GCS;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class GCSErrorMessage implements ErrorMessage {

  static {
    CONSTANTS.put("18", INCORRECT_USERNAME_OR_PASSWORD);
    CONSTANTS.put("fail_connection", INCORRECT_HOST_OR_PORT);
  }

  @Override
  public ConnectorType getConnectorType() {
    return GCS;
  }

}
