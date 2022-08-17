/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_ACCESS_PERMISSION;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_CLUSTER;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT_OR_DATABASE;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.MONGO;

import io.airbyte.integrations.base.errors.utils.ConnectorName;

public class MongoDbErrorMessage extends ErrorMessage {

  {
    ERRORCODES_TYPES.put("-3", INCORRECT_HOST_OR_PORT);
    ERRORCODES_TYPES.put("-4", INCORRECT_CLUSTER);
    ERRORCODES_TYPES.put("13", INCORRECT_ACCESS_PERMISSION);
    ERRORCODES_TYPES.put("18", INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE);
    ERRORCODES_TYPES.put("incorrect_host_or_port_or_database", INCORRECT_HOST_OR_PORT_OR_DATABASE);
  }

  @Override
  public ConnectorName getConnectorName() {
    return MONGO;
  }

}
