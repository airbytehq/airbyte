/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.commons.json.Jsons;
import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreSqlOperations extends JdbcSqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreSqlOperations.class);
  private boolean isLocalFileEnabled = false;

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    database.executeWithinTransaction(queries);
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<PartialAirbyteMessage> records,
                                    final String schemaName,
                                    final String tableName)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }
    verifyLocalFileEnabled(database);
    try {
      final File tmpFile = Files.createTempFile(tableName + "-", ".tmp").toFile();
      loadDataIntoTable(database, records, schemaName, tableName, tmpFile);
      Files.delete(tmpFile.toPath());
    } catch (final IOException e) {
      throw new SQLException(e);
    }
  }

  @Override
  protected void insertRecordsInternalV2(final JdbcDatabase database,
                                         final List<PartialAirbyteMessage> records,
                                         final String schemaName,
                                         final String tableName)
      throws Exception {
    this.insertRecordsInternal(database, records, schemaName, tableName);
  }

  private void loadDataIntoTable(final JdbcDatabase database,
                                 final List<PartialAirbyteMessage> records,
                                 final String schemaName,
                                 final String tmpTableName,
                                 final File tmpFile)
      throws SQLException {
    database.execute(connection -> {
      try {
        writeRecordsToFile(tmpFile, records);
        final String absoluteFile = "'" + tmpFile.getAbsolutePath() + "'";
        final String query = String.format("LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s FIELDS TERMINATED BY " +
            "',' ENCLOSED BY '\"' LINES TERMINATED BY '\\r\\n' NULL DEFINED BY ''", absoluteFile,
            schemaName, tmpTableName);
        try (final Statement stmt = connection.createStatement()) {
          stmt.execute(query);
        }
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  private void writeRecordsToFile(File tmpFile, List<PartialAirbyteMessage> records) throws IOException {
    try (PrintWriter printWriter = new PrintWriter(tmpFile, StandardCharsets.UTF_8);
        final CSVPrinter csvPrinter = new CSVPrinter(printWriter, CSVFormat.DEFAULT)) {
      for (PartialAirbyteMessage r : records) {
        var uuid = UUID.randomUUID().toString();
        var jsonData = r.getSerialized();
        var escapedJsonData = jsonData == null ? null : jsonData.replace("\\", "\\\\");
        var record = r.getRecord();
        var airbyteMeta = record == null ? "" : Jsons.serialize(record.getMeta());
        var extractedAt = record == null ? "" : Timestamp.from(Instant.ofEpochMilli(record.getEmittedAt()));
        if (TypingAndDedupingFlag.isDestinationV2()) {
          csvPrinter.printRecord(uuid, escapedJsonData, extractedAt, "", airbyteMeta);
        } else {
          csvPrinter.printRecord(uuid, escapedJsonData, extractedAt);
        }
      }
    }
  }

  void verifyLocalFileEnabled(final JdbcDatabase database) throws SQLException {
    final boolean localFileEnabled = isLocalFileEnabled || checkIfLocalFileIsEnabled(database);
    if (!localFileEnabled) {
      tryEnableLocalFile(database);
    }
    isLocalFileEnabled = true;
  }

  private void tryEnableLocalFile(final JdbcDatabase database) throws SQLException {
    database.execute(connection -> {
      try (final Statement statement = connection.createStatement()) {
        statement.execute("set global local_infile=true");
      } catch (final Exception e) {
        throw new RuntimeException(
            "The DB user provided to airbyte was unable to switch on the local_infile attribute on the SingleStore server. As an root user, you will need to run \"SET GLOBAL local_infile = true\" before syncing data with Airbyte.",
            e);
      }
    });
  }

  @Override
  public boolean isSchemaRequired() {
    return false;
  }

  private boolean checkIfLocalFileIsEnabled(final JdbcDatabase database) throws SQLException {
    final List<String> localFiles =
        database.queryStrings(connection -> connection.createStatement().executeQuery("SHOW GLOBAL VARIABLES LIKE 'local_infile'"),
            resultSet -> resultSet.getString("Value"));
    return localFiles.get(0).equalsIgnoreCase("on");
  }

  @NotNull
  @Override
  protected String createTableQueryV1(@Nullable String schemaName, @Nullable String tableName) {
    return String.format("""
                         CREATE TABLE IF NOT EXISTS %s.%s (
                         %s VARCHAR(256) PRIMARY KEY,
                         %s JSON,
                         %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
                         SORT KEY (%s));
                         """,
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @NotNull
  @Override
  protected String createTableQueryV2(@Nullable String schemaName, @Nullable String tableName) {
    return String.format("""
                         CREATE TABLE IF NOT EXISTS %s.%s (
                         %s VARCHAR(256) PRIMARY KEY,
                         %s JSON,
                         %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
                         %s TIMESTAMP(6) DEFAULT NULL,
                         %s JSON,
                         SORT KEY (%s));""", schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, JavaBaseConstants.COLUMN_NAME_AB_META,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT);
  }

}
