/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.List;

public class DatabricksSqlOperations extends JdbcSqlOperations {

  @Override
  public void executeTransaction(JdbcDatabase database, List<String> queries) throws Exception {
    for (String query : queries) {
      database.execute(query);
    }
  }

  /**
   * Spark SQL does not support many of the data definition keywords and types as in Postgres.
   * Reference: https://spark.apache.org/docs/latest/sql-ref-datatypes.html
   */
  @Override
  public String createTableQuery(JdbcDatabase database, String schemaName, String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s (%s STRING, %s STRING, %s TIMESTAMP);",
        schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @Override
  public void createSchemaIfNotExists(JdbcDatabase database, String schemaName) throws Exception {
    database.execute(String.format("create database if not exists %s;", schemaName));
  }

  @Override
  public void insertRecordsInternal(JdbcDatabase database,
                                    List<AirbyteRecordMessage> records,
                                    String schemaName,
                                    String tmpTableName) {
    // Do nothing. The records are copied into the table directly from the staging parquet file.
    // So no manual insertion is needed.
  }

}
