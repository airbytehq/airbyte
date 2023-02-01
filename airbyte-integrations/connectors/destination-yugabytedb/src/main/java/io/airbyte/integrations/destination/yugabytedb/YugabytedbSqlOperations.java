/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import com.yugabyte.copy.CopyManager;
import com.yugabyte.core.BaseConnection;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.List;

public class YugabytedbSqlOperations extends JdbcSqlOperations {

  @Override
  protected void insertRecordsInternal(JdbcDatabase database,
                                       List<AirbyteRecordMessage> records,
                                       String schemaName,
                                       String tableName)
      throws Exception {

    if (records.isEmpty()) {
      return;
    }

    File tempFile = null;
    try {
      tempFile = Files.createTempFile(tableName + "-", ".tmp").toFile();
      writeBatchToFile(tempFile, records);

      File finalTempFile = tempFile;
      database.execute(connection -> {

        var copyManager = new CopyManager(connection.unwrap(BaseConnection.class));
        var sql = String.format("COPY %s.%s FROM STDIN DELIMITER ',' CSV", schemaName, tableName);

        try (var bufferedReader = new BufferedReader(new FileReader(finalTempFile, StandardCharsets.UTF_8))) {
          copyManager.copyIn(sql, bufferedReader);
        } catch (IOException e) {
          throw new UncheckedIOException(e);
        }
      });
    } finally {
      if (tempFile != null) {
        Files.delete(tempFile.toPath());
      }
    }
  }

}
