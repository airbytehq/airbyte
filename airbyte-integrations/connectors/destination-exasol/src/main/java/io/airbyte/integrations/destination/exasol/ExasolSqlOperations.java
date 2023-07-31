/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;

public class ExasolSqlOperations extends JdbcSqlOperations {

  public static final String COLUMN_NAME_AB_ID =
      "\"" + JavaBaseConstants.COLUMN_NAME_AB_ID.toUpperCase() + "\"";
  public static final String COLUMN_NAME_DATA =
      "\"" + JavaBaseConstants.COLUMN_NAME_DATA.toUpperCase() + "\"";
  public static final String COLUMN_NAME_EMITTED_AT =
      "\"" + JavaBaseConstants.COLUMN_NAME_EMITTED_AT.toUpperCase() + "\"";

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    String query = String.format("""
                                 CREATE TABLE IF NOT EXISTS %s.%s (
                                   %s VARCHAR(64),
                                   %s VARCHAR(2000000),
                                   %s TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                   PRIMARY KEY(%s)
                                 )""",
        schemaName, tableName,
        ExasolSqlOperations.COLUMN_NAME_AB_ID,
        ExasolSqlOperations.COLUMN_NAME_DATA,
        ExasolSqlOperations.COLUMN_NAME_EMITTED_AT,
        ExasolSqlOperations.COLUMN_NAME_AB_ID);
    LOGGER.info("Create table query: {}", query);
    return query;
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    database.executeWithinTransaction(queries);
  }

  @Override
  protected void insertRecordsInternal(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tableName)
      throws Exception {
    if (records.isEmpty()) {
      return;
    }
    Path tmpFile = createBatchFile(tableName, records);
    try {
      String importStatement = String.format("""
                                             IMPORT INTO %s.%s
                                             FROM LOCAL CSV FILE '%s'
                                             ROW SEPARATOR = 'CRLF'
                                             COLUMN SEPARATOR = ','""", schemaName, tableName, tmpFile.toAbsolutePath());
      LOGGER.info("IMPORT statement: {}", importStatement);
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
