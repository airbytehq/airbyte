/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.clickhouse.client.ClickHouseFormat;
import com.clickhouse.jdbc.ClickHouseConnection;
import com.clickhouse.jdbc.ClickHouseStatement;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseSqlOperations extends JdbcSqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseSqlOperations.class);

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
            + "%s DateTime64(3, 'GMT') DEFAULT now(),\n"
            + "PRIMARY KEY(%s)\n"
            + ")\n"
            + "ENGINE = MergeTree;\n",
        schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
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

        final ClickHouseConnection conn = connection.unwrap(ClickHouseConnection.class);
        final ClickHouseStatement sth = conn.createStatement();
        sth.write() // Write API entrypoint
            .table(String.format("%s.%s", schemaName, tmpTableName)) // where to write data
            .format(ClickHouseFormat.CSV) // set a format
            .data(tmpFile.getAbsolutePath()) // specify input
            .send();

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
