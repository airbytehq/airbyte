/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static java.lang.String.format;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.List;

public class StarburstGalaxySqlOperations
    extends JdbcSqlOperations {

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    for (final String query : queries) {
      database.execute(query);
    }
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    String createTable = format(
        "CREATE TABLE IF NOT EXISTS %s.%s (%s VARCHAR, %s VARCHAR, %s TIMESTAMP(6)) WITH (format = 'PARQUET', type = 'ICEBERG')",
        schemaName,
        tableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    LOGGER.info("Create table: {}", createTable);
    return createTable;
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    String createSchema = format("CREATE SCHEMA IF NOT EXISTS %s", schemaName);
    LOGGER.info("Create schema if not exists: {}", createSchema);
    database.execute(createSchema);
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<AirbyteRecordMessage> records,
                                    final String schemaName,
                                    final String tmpTableName) {
    // Do nothing. The records are copied into the table directly from the staging parquet file.
    // So no manual insertion is needed.
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    database.execute(format("DROP TABLE IF EXISTS %s.%s", schemaName, tableName));
  }

}
