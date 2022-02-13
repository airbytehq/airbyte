/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcSqlOperations.class);
  protected static final String SHOW_SCHEMAS = "show schemas;";
  protected static final String NAME = "name";

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    if (!isSchemaExists(database, schemaName)) {
      AirbyteSentry.executeWithTracing("CreateSchema",
          () -> database.execute(createSchemaQuery(schemaName)),
          Map.of("schema", schemaName));
    }
  }

  private String createSchemaQuery(final String schemaName) {
    return String.format("CREATE SCHEMA IF NOT EXISTS %s;\n", schemaName);
  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    AirbyteSentry.executeWithTracing("CreateTableIfNotExists",
        () -> database.execute(createTableQuery(database, schemaName, tableName)),
        Map.of("schema", Objects.requireNonNullElse(schemaName, "null"), "table", tableName));
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR PRIMARY KEY,\n"
            + "%s JSONB,\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
            + ");\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  protected void writeBatchToFile(final File tmpFile, final List<AirbyteRecordMessage> records) throws Exception {
    PrintWriter writer = null;
    try {
      writer = new PrintWriter(tmpFile, StandardCharsets.UTF_8);
      final var csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT);

      for (final AirbyteRecordMessage record : records) {
        final var uuid = UUID.randomUUID().toString();
        final var jsonData = Jsons.serialize(formatData(record.getData()));
        final var emittedAt = Timestamp.from(Instant.ofEpochMilli(record.getEmittedAt()));
        csvPrinter.printRecord(uuid, jsonData, emittedAt);
      }
    } finally {
      if (writer != null) {
        writer.close();
      }
    }
  }

  protected JsonNode formatData(final JsonNode data) {
    return data;
  }

  @Override
  public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format("TRUNCATE TABLE %s.%s;\n", schemaName, tableName);
  }

  @Override
  public String copyTableQuery(final JdbcDatabase database, final String schemaName, final String srcTableName, final String dstTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", schemaName, dstTableName, schemaName, srcTableName);
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    final StringBuilder appendedQueries = new StringBuilder();
    appendedQueries.append("BEGIN;\n");
    for (final String query : queries) {
      appendedQueries.append(query);
    }
    appendedQueries.append("COMMIT;");
    AirbyteSentry.executeWithTracing("ExecuteTransactions",
        () -> database.execute(appendedQueries.toString()),
        Map.of("queries", queries));
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    AirbyteSentry.executeWithTracing("DropTableIfExists",
        () -> database.execute(dropTableIfExistsQuery(schemaName, tableName)),
        Map.of("schema", Objects.requireNonNullElse(schemaName, "null"), "table", tableName));
  }

  private String dropTableIfExistsQuery(final String schemaName, final String tableName) {
    return String.format("DROP TABLE IF EXISTS %s.%s;\n", schemaName, tableName);
  }

  @Override
  public boolean isSchemaRequired() {
    return true;
  }

  @Override
  public boolean isValidData(final JsonNode data) {
    return true;
  }

  @Override
  public final void insertRecords(final JdbcDatabase database,
                                  final List<AirbyteRecordMessage> records,
                                  final String schemaName,
                                  final String tableName)
      throws Exception {
    AirbyteSentry.executeWithTracing("InsertRecords",
        () -> {
          records.forEach(airbyteRecordMessage -> getDataAdapter().adapt(airbyteRecordMessage.getData()));
          insertRecordsInternal(database, records, schemaName, tableName);
        },
        Map.of("schema", Objects.requireNonNullElse(schemaName, "null"), "table", tableName, "recordCount", records.size()));
  }

  protected abstract void insertRecordsInternal(JdbcDatabase database,
                                                List<AirbyteRecordMessage> records,
                                                String schemaName,
                                                String tableName)
      throws Exception;

  protected DataAdapter getDataAdapter() {
    return new DataAdapter(j -> false, c -> c);
  }

}
