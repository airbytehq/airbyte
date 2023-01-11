/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;

public class ExasolSqlOperations extends JdbcSqlOperations {

  public static final String COLUMN_NAME_AB_ID =
      "\"" + JavaBaseConstants.COLUMN_NAME_AB_ID.toUpperCase() + "\"";
  public static final String COLUMN_NAME_DATA =
      "\"" + JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase() + "\"";
  public static final String COLUMN_NAME_EMITTED_AT =
      "\"" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT.toUpperCase() + "\"";

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR(64),\n"
            + "%s VARCHAR(2000000),\n"
            + "%s TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n"
            + "PRIMARY KEY(%s)\n"
            + ")\n",
        schemaName, tableName,
        ExasolSqlOperations.COLUMN_NAME_AB_ID,
        ExasolSqlOperations.COLUMN_NAME_DATA,
        ExasolSqlOperations.COLUMN_NAME_EMITTED_AT,
        ExasolSqlOperations.COLUMN_NAME_AB_ID);
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    // Note: Exasol does not support multi query
    for (final String query : queries) {
      database.execute(query);
    }
  }

  @Override
  protected void insertRecordsInternal(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tableName) throws Exception {
    if (records.isEmpty()) {
      return;
    }
    Path tmpFile = createBatchFile(tableName, records);
    try {
      String importStatement = String.format("""
             IMPORT INTO %s.%s
             FROM LOCAL CSV FILE '%s'
             ROW SEPARATOR = 'CRLF'
             COLUMN SEPARATOR = ','\s""", schemaName, tableName, tmpFile.toAbsolutePath().toString());
      database.execute(connection -> connection.createStatement().execute(importStatement));
    } finally {
      Files.delete(tmpFile);
    }
  }

  private Path createBatchFile(String tableName, List<AirbyteRecordMessage> records) throws Exception {
    Path tmpFile = Files.createTempFile(tableName + "-", ".tmp");
    writeBatchToFile(tmpFile.toFile(), records);
    return tmpFile;
  }
}
