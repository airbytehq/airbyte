/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.jdbc.SqlOperations;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SqlServerOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(SqlServerOperations.class);
  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    final String query = String.format("IF NOT EXISTS ( SELECT * FROM sys.schemas WHERE name = '%s') EXEC('CREATE SCHEMA [%s]')",
        schemaName,
        schemaName);
    database.execute(query);
  }

  @Override
  public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) throws Exception {
    database.execute(createTableQuery(database, schemaName, tableName));
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "IF NOT EXISTS (SELECT * FROM sys.tables t JOIN sys.schemas s ON t.schema_id = s.schema_id "
            + "WHERE s.name = '%s' AND t.name = '%s') "
            + "CREATE TABLE %s.%s ( \n"
            + "%s VARCHAR(64) PRIMARY KEY,\n"
            + "%s NVARCHAR(MAX),\n" // Microsoft SQL Server specific: NVARCHAR can store Unicode meanwhile VARCHAR - not
            + "%s DATETIMEOFFSET(7) DEFAULT SYSDATETIMEOFFSET(),\n"
            + "%s DATETIMEOFFSET(7),\n"
            + "%s NVARCHAR(MAX),\n"
            + ");\n",
        schemaName, tableName, schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, JavaBaseConstants.COLUMN_NAME_AB_META);
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName) throws Exception {
    final String query = String.format(
        "IF EXISTS (SELECT * FROM sys.tables t JOIN sys.schemas s ON t.schema_id = s.schema_id "
            + "WHERE s.name = '%s' AND t.name = '%s') "
            + "DROP TABLE %s.%s",
        schemaName, tableName, schemaName, tableName);
    database.execute(query);
  }

  @Override
  public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format("TRUNCATE TABLE %s.%s\n", schemaName, tableName);
  }

  @Override
  public void insertRecords(final JdbcDatabase database,
                            final List<PartialAirbyteMessage> records,
                            final String schemaName,
                            final String tempTableName)
      throws SQLException {
    // MSSQL has a limitation of 2100 parameters used in a query
    // Airbyte inserts data with 3 columns (raw table) this limits to 700 records.
    // Limited the variable to 500 records to
    final int MAX_BATCH_SIZE = 400;
    final String insertQueryComponent = String.format(
        "INSERT INTO %s.%s (%s, %s, %s, %s, %s) VALUES\n",
        schemaName,
        tempTableName,
        JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
        JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
        JavaBaseConstants.COLUMN_NAME_AB_META);
    final String recordQueryComponent = "(?, ?, ?, ?, ?),\n";
    final List<List<PartialAirbyteMessage>> batches = Lists.partition(records, MAX_BATCH_SIZE);
    for (List<PartialAirbyteMessage> batch : batches) {
      if (batch.isEmpty()) {
        continue;
      }
      database.execute(connection -> {
        final StringBuilder sqlStatement = new StringBuilder(insertQueryComponent);
        for (PartialAirbyteMessage ignored : batch) {
          sqlStatement.append(recordQueryComponent);
        }
        final var sql = sqlStatement.substring(0, sqlStatement.length() - 2) + ";";
        try (final var statement = connection.prepareStatement(sql)) {
          int i = 1;
          for (PartialAirbyteMessage record : batch) {
            final var id = UUID.randomUUID().toString();
            statement.setString(i++, id);
            statement.setString(i++, record.getSerialized());
            statement.setTimestamp(i++, Timestamp.from(Instant.ofEpochMilli(Objects.requireNonNull(record.getRecord()).getEmittedAt())));
            statement.setTimestamp(i++, null);
            String metadata;
            if (record.getRecord().getMeta() != null) {
              try {
                metadata = OBJECT_MAPPER.writeValueAsString(record.getRecord().getMeta());
              } catch (Exception e) {
                LOGGER.error("Failed to serialize record metadata for record {}", id, e);
                metadata = null;
              }
            } else {
              metadata = null;
            }
            statement.setString(i++, metadata);
          }
          statement.execute();
        }
      });
    }
  }

  @Override
  public String insertTableQuery(final JdbcDatabase database,
                                 final String schemaName,
                                 final String sourceTableName,
                                 final String destinationTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", schemaName, destinationTableName, schemaName, sourceTableName);
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    database.execute("BEGIN TRAN;\n" + String.join("\n", queries) + "\nCOMMIT TRAN;");
  }

  @Override
  public boolean isValidData(final JsonNode data) {
    return true;
  }

  @Override
  public boolean isSchemaRequired() {
    return true;
  }

}
