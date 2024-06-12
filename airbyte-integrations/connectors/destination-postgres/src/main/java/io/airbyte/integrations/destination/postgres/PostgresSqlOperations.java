/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.*;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import org.apache.commons.lang3.StringUtils;
import org.postgresql.copy.CopyManager;
import org.postgresql.core.BaseConnection;

public class PostgresSqlOperations extends JdbcSqlOperations {

  public PostgresSqlOperations() {}

  @Override
  protected List<String> postCreateTableQueries(final String schemaName, final String tableName) {
    if (TypingAndDedupingFlag.isDestinationV2()) {
      return List.of(
          // the raw_id index _could_ be unique (since raw_id is a UUID)
          // but there's no reason to do that (because it's a UUID :P )
          // and it would just slow down inserts.
          // also, intentionally don't specify the type of index (btree, hash, etc). Just use the default.
          "CREATE INDEX IF NOT EXISTS " + tableName + "_raw_id" + " ON " + schemaName + "." + tableName + "(_airbyte_raw_id)",
          "CREATE INDEX IF NOT EXISTS " + tableName + "_extracted_at" + " ON " + schemaName + "." + tableName + "(_airbyte_extracted_at)",
          "CREATE INDEX IF NOT EXISTS " + tableName + "_loaded_at" + " ON " + schemaName + "." + tableName
              + "(_airbyte_loaded_at, _airbyte_extracted_at)");
    } else {
      return Collections.emptyList();
    }
  }

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

}
