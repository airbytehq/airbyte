/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.vertica;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.File;
import java.io.FileWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

public class VerticaSqlOperations extends JdbcSqlOperations {

  protected void writeBatchToFile(final File tmpFile, final List<AirbyteRecordMessage> records) throws Exception {
    try {
      final StringBuffer bfr = new StringBuffer();
      FileWriter wr = new FileWriter(tmpFile, StandardCharsets.UTF_8);
      for (AirbyteRecordMessage record : records) {
        final var uuid = UUID.randomUUID().toString();
        final var jsonData = Jsons.serialize(formatData(record.getData()));
        final var emittedAt = Timestamp.from(Instant.ofEpochMilli(record.getEmittedAt()));
        wr.write(uuid.toString() + "|" + jsonData.toString() + "|" + emittedAt.toString() + "\n");
      }
      wr.close();
    } catch (Exception e) {}
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
        tmpFile = Files.createTempFile(tmpTableName + "-", ".csv").toFile();
        writeBatchToFile(tmpFile, records);
        final String query = String.format("copy %s.%s from local '%s' delimiter '%s'", schemaName, tmpTableName, tmpFile, "|");
        Statement stmt = connection.createStatement();
        stmt.execute(query);
        stmt.close();
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    final String query = String.format("CREATE SCHEMA IF NOT EXISTS %s", schemaName);
    database.execute(query);
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    final String query = String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s (%s VARCHAR(500) PRIMARY KEY,%s VARCHAR(1000),%s VARCHAR(1000));", schemaName, tableName,
        VerticaDestination.COLUMN_NAME_AB_ID, VerticaDestination.COLUMN_NAME_DATA, VerticaDestination.COLUMN_NAME_EMITTED_AT);
    return query;
  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) {
    try {
      database.execute(createTableQuery(database, schemaName, tableName));
    } catch (final Exception e) {
      LOGGER.error("Error while creating table.", e);
    }
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName) {
    try {
      final String query = String.format("DROP TABLE IF EXISTS %s.%s", schemaName, tableName);
      database.execute(query);
    } catch (Exception e) {
      LOGGER.error(String.format("Error dropping table %s.%s", schemaName, tableName), e);
      throw new RuntimeException(e);
    }
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    database.executeWithinTransaction(queries);
  }

  @Override
  public String insertTableQuery(final JdbcDatabase database,
                                 final String schemaName,
                                 final String sourceTableName,
                                 final String destinationTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", schemaName, destinationTableName, schemaName, sourceTableName);
  }

}
