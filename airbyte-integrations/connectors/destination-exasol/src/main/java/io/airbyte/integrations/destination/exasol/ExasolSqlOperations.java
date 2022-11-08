/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import com.exasol.jdbc.EXAConnection;
import com.exasol.jdbc.EXAStatement;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
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
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR(2000000),\n"
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
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<AirbyteRecordMessage> records,
                                    final String schemaName,
                                    final String tmpTableName)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }

    database.execute(connection -> {
      File tmpFile = null;
      try {
        tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
        writeBatchToFile(tmpFile, records);


        final EXAConnection conn = connection.unwrap(EXAConnection.class);
        final EXAStatement stmt = (EXAStatement) conn.createStatement();

        stmt.execute(String.format("""
                IMPORT INTO %s.%s
                FROM LOCAL CSV FILE '%s'
                COLUMN SEPARATOR = ','\s""", schemaName, tmpTableName, tmpFile.getAbsolutePath()));

      } catch (final Exception e) {
        throw new RuntimeException(e);
      } finally {
        try {
          if (tmpFile != null) {
            Files.delete(tmpFile.toPath());
          }
        } catch (final IOException e) {
          throw new RuntimeException(e);
        }
      }
    });
  }

}
