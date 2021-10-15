/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class SnowflakeSqlOperations extends JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeSqlOperations.class);

  @Override
  public void createTableIfNotExists(JdbcDatabase database, String schemaName, String tableName) throws SQLException {
    final String createTableQuery = String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR PRIMARY KEY,\n"
            + "%s VARIANT,\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT current_timestamp()\n"
            + ") data_retention_time_in_days = 0;",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    database.execute(createTableQuery);
  }

  @Override
  public void insertRecordsInternal(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tableName)
      throws SQLException {
    LOGGER.info("actual size of batch: {}", records.size());

    // snowflake query syntax:
    // requires selecting from a set of values in order to invoke the parse_json function.
    // INSERT INTO public.users (ab_id, data, emitted_at) SELECT column1, parse_json(column2), column3
    // FROM VALUES
    // (?, ?, ?),
    // ...
    final String insertQuery = String.format(
        "INSERT INTO %s.%s (%s, %s, %s) SELECT column1, parse_json(column2), column3 FROM VALUES\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    final String recordQuery = "(?, ?, ?),\n";
    SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQuery, recordQuery, database, records);
  }

}
