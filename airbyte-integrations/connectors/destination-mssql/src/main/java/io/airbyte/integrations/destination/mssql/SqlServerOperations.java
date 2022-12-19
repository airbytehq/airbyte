/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.List;

public class SqlServerOperations implements SqlOperations {

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
            + "%s DATETIMEOFFSET(7) DEFAULT SYSDATETIMEOFFSET()\n"
            + ");\n",
        schemaName, tableName, schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
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
                            final List<AirbyteRecordMessage> records,
                            final String schemaName,
                            final String tempTableName)
      throws SQLException {
    // MSSQL has a limitation of 2100 parameters used in a query
    // Airbyte inserts data with 3 columns (raw table) this limits to 700 records.
    // Limited the variable to 500 records to
    final int MAX_BATCH_SIZE = 500;
    final String insertQueryComponent = String.format(
        "INSERT INTO %s.%s (%s, %s, %s) VALUES\n",
        schemaName,
        tempTableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
    final String recordQueryComponent = "(?, ?, ?),\n";
    final List<List<AirbyteRecordMessage>> batches = Lists.partition(records, MAX_BATCH_SIZE);
    batches.forEach(record -> {
      try {
        SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, database, record);
      } catch (final SQLException e) {
        e.printStackTrace();
      }
    });
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
