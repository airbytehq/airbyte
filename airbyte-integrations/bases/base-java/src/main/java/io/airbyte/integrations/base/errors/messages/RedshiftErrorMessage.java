/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_ACCESS_PERMISSION;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.REDSHIFT;

import io.airbyte.integrations.base.errors.utils.ConnectorName;

public class RedshiftErrorMessage extends ErrorMessage {

  {
    ERRORCODES_TYPES.put("28000", INCORRECT_USERNAME_OR_PASSWORD);
    ERRORCODES_TYPES.put("HY000", INCORRECT_HOST_OR_PORT);
    ERRORCODES_TYPES.put("3D000", INCORRECT_DB_NAME);
    ERRORCODES_TYPES.put("42501", INCORRECT_ACCESS_PERMISSION);
  }

  @Override
  public ConnectorName getConnectorName() {
    return REDSHIFT;
  }

}
