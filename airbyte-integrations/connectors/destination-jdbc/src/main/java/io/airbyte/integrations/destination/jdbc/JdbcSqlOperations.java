/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

@SuppressWarnings("OptionalUsedAsFieldOrParameterType")
public abstract class JdbcSqlOperations implements SqlOperations {

  protected static final String SHOW_SCHEMAS = "show schemas;";
  protected static final String NAME = "name";

  // this adapter modifies record message before inserting them to the destination
  protected final Optional<DataAdapter> dataAdapter;
  private final Set<String> schemaSet = new HashSet<>();

  protected JdbcSqlOperations() {
    this.dataAdapter = Optional.empty();
  }

  protected JdbcSqlOperations(final DataAdapter dataAdapter) {
    this.dataAdapter = Optional.of(dataAdapter);
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    try {
      if (!schemaSet.contains(schemaName) && !isSchemaExists(database, schemaName)) {
        database.execute(String.format("CREATE SCHEMA IF NOT EXISTS %s;", schemaName));
        schemaSet.add(schemaName);
      }
    } catch (Exception e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  /**
   * When an exception occurs, we may recognize it as an issue with the users permissions
   * or other configuration options. In these cases, we can wrap the exception in a {@link ConfigErrorException}
   * which will exclude the error from our on-call paging/reporting
   * @param e the exception to check.
   * @return A ConfigErrorException with a message with actionable feedback to the user.
   */
  protected Optional<ConfigErrorException> checkForKnownConfigExceptions(Exception e) {
    return Optional.empty();
  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    try {
      database.execute(createTableQuery(database, schemaName, tableName));
    } catch (SQLException e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
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
    try (final PrintWriter writer = new PrintWriter(tmpFile, StandardCharsets.UTF_8);
        final CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT)) {
      for (final AirbyteRecordMessage record : records) {
        final var uuid = UUID.randomUUID().toString();
        final var jsonData = Jsons.serialize(formatData(record.getData()));
        final var emittedAt = Timestamp.from(Instant.ofEpochMilli(record.getEmittedAt()));
        csvPrinter.printRecord(uuid, jsonData, emittedAt);
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
  public String insertTableQuery(final JdbcDatabase database, final String schemaName, final String srcTableName, final String dstTableName) {
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
    database.execute(appendedQueries.toString());
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName) throws SQLException {
    database.execute(dropTableIfExistsQuery(schemaName, tableName));
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
    dataAdapter.ifPresent(adapter -> records.forEach(airbyteRecordMessage -> adapter.adapt(airbyteRecordMessage.getData())));
    insertRecordsInternal(database, records, schemaName, tableName);
  }

  protected abstract void insertRecordsInternal(JdbcDatabase database,
                                                List<AirbyteRecordMessage> records,
                                                String schemaName,
                                                String tableName)
      throws Exception;

}
