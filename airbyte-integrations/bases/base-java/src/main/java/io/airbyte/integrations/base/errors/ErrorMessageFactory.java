/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors;

import static io.airbyte.integrations.base.errors.utils.ConnectorName.DEFAULT;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.GCS;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.MONGO;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.MSSQL;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.MYSQL;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.ORACLE;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.POSTGRES;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.REDSHIFT;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.SNOWFLAKE;

import io.airbyte.integrations.base.errors.messages.DefaultErrorMessage;
import io.airbyte.integrations.base.errors.messages.ErrorMessage;
import io.airbyte.integrations.base.errors.messages.GcsErrorMessage;
import io.airbyte.integrations.base.errors.messages.MongoDbErrorMessage;
import io.airbyte.integrations.base.errors.messages.MssqlErrorMessage;
import io.airbyte.integrations.base.errors.messages.MysqlErrorMessage;
import io.airbyte.integrations.base.errors.messages.OracleErrorMessage;
import io.airbyte.integrations.base.errors.messages.PostgresErrorMessage;
import io.airbyte.integrations.base.errors.messages.RedshiftErrorMessage;
import io.airbyte.integrations.base.errors.messages.SnowflakeErrorMessage;
import io.airbyte.integrations.base.errors.utils.ConnectorName;
import java.util.Map;

public class ErrorMessageFactory {

  private final static Map<ConnectorName, ErrorMessage> CONNECTOR_ERROR_MESSAGE_MAP = Map.of(MSSQL, new MssqlErrorMessage(),
      MYSQL, new MysqlErrorMessage(),
      POSTGRES, new PostgresErrorMessage(),
      ORACLE, new OracleErrorMessage(),
      MONGO, new MongoDbErrorMessage(),
      REDSHIFT, new RedshiftErrorMessage(),
      GCS, new GcsErrorMessage(),
      SNOWFLAKE, new SnowflakeErrorMessage(),
      DEFAULT, new DefaultErrorMessage());

  public static ErrorMessage getErrorMessage(ConnectorName name) {
    if (CONNECTOR_ERROR_MESSAGE_MAP.containsKey(name)) {
      return CONNECTOR_ERROR_MESSAGE_MAP.get(name);
    }
    return CONNECTOR_ERROR_MESSAGE_MAP.get(DEFAULT);
  }

}
