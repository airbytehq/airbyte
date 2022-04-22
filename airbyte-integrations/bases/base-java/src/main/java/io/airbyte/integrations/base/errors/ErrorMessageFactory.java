/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors;

import static io.airbyte.integrations.base.errors.utils.ConnectorType.MONGO;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.MSSQL;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.MYSQL;
import static io.airbyte.integrations.base.errors.utils.ConnectorType.POSTGRES;

import io.airbyte.integrations.base.errors.messages.DefaultErrorMessage;
import io.airbyte.integrations.base.errors.messages.ErrorMessage;
import io.airbyte.integrations.base.errors.messages.MongoDBErrorMessage;
import io.airbyte.integrations.base.errors.messages.MsSQLErrorMessage;
import io.airbyte.integrations.base.errors.messages.MySQLErrorMessage;
import io.airbyte.integrations.base.errors.messages.PostgresErrorMessage;
import io.airbyte.integrations.base.errors.utils.ConnectorType;
import java.util.Map;

public class ErrorMessageFactory {

  private final static Map<ConnectorType, ErrorMessage> MAP = Map.of(MSSQL, new MsSQLErrorMessage(),
      MYSQL, new MySQLErrorMessage(),
      POSTGRES, new PostgresErrorMessage(),
      MONGO, new MongoDBErrorMessage(),
      ConnectorType.DEFAULT, new DefaultErrorMessage());

  public static ErrorMessage getErrorMessage(ConnectorType type) {
    if (MAP.containsKey(type)) {
      return MAP.get(type);
    }
    return MAP.get(ConnectorType.DEFAULT);
  }

}
