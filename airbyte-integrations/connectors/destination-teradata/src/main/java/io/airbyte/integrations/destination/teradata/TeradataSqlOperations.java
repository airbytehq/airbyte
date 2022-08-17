/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.List;


public class TeradataSqlOperations extends JdbcSqlOperations {
    public TeradataSqlOperations() {
        super(new TeradataDataAdapter());
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
        System.out.println("tmpTableName : " + tmpTableName);
        
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

