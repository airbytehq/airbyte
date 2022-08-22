/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_ACCESS_PERMISSION;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_CLUSTER;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.MONGO;

import io.airbyte.integrations.base.errors.utils.ConnectorName;

public class MongoDbErrorMessage extends ErrorMessage {

  {
    ERROR_CODES_TYPES.put("-3", INCORRECT_HOST_OR_PORT);
    ERROR_CODES_TYPES.put("-4", INCORRECT_CLUSTER);
    ERROR_CODES_TYPES.put("13", INCORRECT_ACCESS_PERMISSION);
    ERROR_CODES_TYPES.put("18", INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE);
  }

  @Override
  public ConnectorName getConnectorName() {
    return MONGO;
  }

}
