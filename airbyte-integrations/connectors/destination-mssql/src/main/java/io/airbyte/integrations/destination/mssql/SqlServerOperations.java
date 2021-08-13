/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.destination.mssql;

import com.google.common.collect.Lists;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.sql.SQLException;
import java.util.List;

public class SqlServerOperations implements SqlOperations {

  @Override
  public void createSchemaIfNotExists(JdbcDatabase database, String schemaName) throws Exception {
    final String query = String.format("IF NOT EXISTS ( SELECT * FROM sys.schemas WHERE name = '%s') EXEC('CREATE SCHEMA [%s]')",
        schemaName,
        schemaName);
    database.execute(query);
  }

  @Override
  public void createTableIfNotExists(JdbcDatabase database, String schemaName, String tableName) throws Exception {
    database.execute(createTableQuery(database, schemaName, tableName));
  }

  @Override
  public String createTableQuery(JdbcDatabase database, String schemaName, String tableName) {
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
  public void dropTableIfExists(JdbcDatabase database, String schemaName, String tableName) throws Exception {
    final String query = String.format(
        "IF EXISTS (SELECT * FROM sys.tables t JOIN sys.schemas s ON t.schema_id = s.schema_id "
            + "WHERE s.name = '%s' AND t.name = '%s') "
            + "DROP TABLE %s.%s",
        schemaName, tableName, schemaName, tableName);
    database.execute(query);
  }

  @Override
  public String truncateTableQuery(JdbcDatabase database, String schemaName, String tableName) {
    return String.format("TRUNCATE TABLE %s.%s\n", schemaName, tableName);
  }

  @Override
  public void insertRecords(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tempTableName) throws SQLException {
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
      } catch (SQLException e) {
        e.printStackTrace();
      }
    });
  }

  @Override
  public String copyTableQuery(JdbcDatabase database, String schemaName, String sourceTableName, String destinationTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", schemaName, destinationTableName, schemaName, sourceTableName);
  }

  @Override
  public void executeTransaction(JdbcDatabase database, List<String> queries) throws Exception {
    database.execute("BEGIN TRAN;\n" + String.join("\n", queries) + "\nCOMMIT TRAN;");
  }

  @Override
  public boolean isValidData(String data) {
    return true;
  }

  @Override
  public boolean isSchemaRequired() {
    return true;
  }

}
