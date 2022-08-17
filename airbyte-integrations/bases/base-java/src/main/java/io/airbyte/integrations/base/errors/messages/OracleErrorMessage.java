/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_ACCOUNT_IS_LOCKED;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE_OR_USER_ACCESS_DENIED;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.ORACLE;

import io.airbyte.integrations.base.errors.utils.ConnectorName;

public class OracleErrorMessage extends ErrorMessage {

  {
    ERRORCODES_TYPES.put("99999", INCORRECT_USERNAME_ACCOUNT_IS_LOCKED);
    ERRORCODES_TYPES.put("72000", INCORRECT_USERNAME_OR_PASSWORD_OR_DATABASE_OR_USER_ACCESS_DENIED);
    ERRORCODES_TYPES.put("08006", INCORRECT_HOST_OR_PORT);
  }

  @Override
  public ConnectorName getConnectorName() {
    return ORACLE;
  }

}
