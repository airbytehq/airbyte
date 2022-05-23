/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_ACCESS_PERMISSION;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_CLUSTER;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT_OR_DATABASE;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.MONGO;

import io.airbyte.integrations.base.errors.utils.ConnectorType;

public class MongoDbErrorMessage extends ErrorMessage {

  {
    CONSTANTS.put("-3", INCORRECT_HOST_OR_PORT);
    CONSTANTS.put("-4", INCORRECT_CLUSTER);
    CONSTANTS.put("13", INCORRECT_ACCESS_PERMISSION);
    CONSTANTS.put("18", INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE);
    CONSTANTS.put("incorrect_host_or_port_or_database", INCORRECT_HOST_OR_PORT_OR_DATABASE);
  }

  @Override
  public ConnectorType getConnectorType() {
    return MONGO;
  }

}
