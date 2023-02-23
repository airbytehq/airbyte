/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bytehouse;

import com.bytedance.bytehouse.jdbc.ByteHouseConnection;
import com.bytedance.bytehouse.jdbc.statement.ByteHouseStatement;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;

public class BytehouseSqlOperations extends JdbcSqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(BytehouseSqlOperations.class);

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    database.execute(String.format("CREATE DATABASE IF NOT EXISTS %s;\n", schemaName));
  }

  @Override
  public boolean isSchemaRequired() {
    return false;
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s String,\n"
            + "%s String,\n"
            + "%s DateTime64(3, 'GMT') DEFAULT now()\n"
            + ")\n"
            + "ENGINE = CnchMergeTree\n"
            + "ORDER BY %s\n"
            + "PRIMARY KEY %s;\n",
        schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_AB_ID);
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    // Note: ClickHouse does not support multi query
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
    LOGGER.info("actual size of batch: {}", records.size());

    if (records.isEmpty()) {
      return;
    }

    database.execute(connection -> {
      File tmpFile = null;
      Exception primaryException = null;
      try {
        tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
        writeBatchToFile(tmpFile, records);

        final ByteHouseConnection conn = connection.unwrap(ByteHouseConnection.class);
        final ByteHouseStatement sth = (ByteHouseStatement) conn.createStatement();
        try (Statement stmt = connection.createStatement()) {
          final String insertSql = String.format("INSERT INTO %s.%s FORMAT csv INFILE '%s'", schemaName, tmpTableName, tmpFile.getAbsolutePath());
          stmt.executeUpdate(insertSql);
        } catch (SQLException ex) {
          ex.printStackTrace();
        }
      } catch (final Exception e) {
        primaryException = e;
        throw new RuntimeException(e);
      } finally {
        try {
          if (tmpFile != null) {
            Files.delete(tmpFile.toPath());
          }
        } catch (final IOException e) {
          if (primaryException != null)
            e.addSuppressed(primaryException);
          throw new RuntimeException(e);
        }
      }
    });
  }

}
