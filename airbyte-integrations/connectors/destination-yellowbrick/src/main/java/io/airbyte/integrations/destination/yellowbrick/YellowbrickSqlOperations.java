/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.*;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.List;
import org.apache.commons.lang3.StringUtils;
import org.postgresql.copy.CopyManager;
import org.postgresql.core.BaseConnection;

public class YellowbrickSqlOperations extends JdbcSqlOperations {

  public static final int YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE = 64000;

  public YellowbrickSqlOperations() {}

  @Override
  protected void insertRecordsInternalV2(final JdbcDatabase database,
                                         final List<PartialAirbyteMessage> records,
                                         final String schemaName,
                                         final String tableName)
      throws Exception {
    insertRecordsInternal(database, records, schemaName, tableName,
        COLUMN_NAME_AB_RAW_ID,
        COLUMN_NAME_DATA,
        COLUMN_NAME_AB_EXTRACTED_AT,
        COLUMN_NAME_AB_LOADED_AT,
        COLUMN_NAME_AB_META);
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<PartialAirbyteMessage> records,
                                    final String schemaName,
                                    final String tmpTableName)
      throws SQLException {
    insertRecordsInternal(database, records, schemaName, tmpTableName, COLUMN_NAME_AB_ID, COLUMN_NAME_DATA, COLUMN_NAME_EMITTED_AT);
  }

  private void insertRecordsInternal(final JdbcDatabase database,
                                     final List<PartialAirbyteMessage> records,
                                     final String schemaName,
                                     final String tmpTableName,
                                     final String... columnNames)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }
    // Explicitly passing column order to avoid order mismatches between CREATE TABLE and COPY statement
    final String orderedColumnNames = StringUtils.join(columnNames, ", ");
    database.execute(connection -> {
      File tmpFile = null;
      try {
        tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
        writeBatchToFile(tmpFile, records);

        final var copyManager = new CopyManager(connection.unwrap(BaseConnection.class));
        final var sql = String.format("COPY %s.%s (%s) FROM stdin DELIMITER ',' CSV", schemaName, tmpTableName, orderedColumnNames);
        final var bufferedReader = new BufferedReader(new FileReader(tmpFile, StandardCharsets.UTF_8));
        copyManager.copyIn(sql, bufferedReader);
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

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR(100) PRIMARY KEY,\n"
            + "%s VARCHAR(%s),\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,\n"
            + "%s TIMESTAMP WITH TIME ZONE NULL,\n"
            + "%s VARCHAR(%s)\n"
            + ");\n",
        schemaName, tableName, COLUMN_NAME_AB_RAW_ID, COLUMN_NAME_DATA, YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE,
        COLUMN_NAME_AB_EXTRACTED_AT, COLUMN_NAME_AB_LOADED_AT, COLUMN_NAME_AB_META, YELLOWBRICK_VARCHAR_MAX_BYTE_SIZE);
  }

}
