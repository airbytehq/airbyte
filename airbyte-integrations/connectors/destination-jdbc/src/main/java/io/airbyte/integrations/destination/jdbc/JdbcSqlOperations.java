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

package io.airbyte.integrations.destination.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class JdbcSqlOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcSqlOperations.class);

  @Override
  public void createSchemaIfNotExists(JdbcDatabase database, String schemaName) throws Exception {
    database.execute(createSchemaQuery(schemaName));
  }

  private String createSchemaQuery(String schemaName) {
    return String.format("CREATE SCHEMA IF NOT EXISTS %s;\n", schemaName);
  }

  @Override
  public void createTableIfNotExists(JdbcDatabase database, String schemaName, String tableName) throws SQLException {
    database.execute(createTableQuery(database, schemaName, tableName));
  }

  @Override
  public String createTableQuery(JdbcDatabase database, String schemaName, String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR PRIMARY KEY,\n"
            + "%s JSONB,\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
            + ");\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  protected void writeBatchToFile(File tmpFile, List<AirbyteRecordMessage> records) throws Exception {
    PrintWriter writer = null;
    try {
      writer = new PrintWriter(tmpFile, StandardCharsets.UTF_8);
      var csvPrinter = new CSVPrinter(writer, CSVFormat.DEFAULT);

      for (AirbyteRecordMessage record : records) {
        var uuid = UUID.randomUUID().toString();
        var jsonData = Jsons.serialize(formatData(record.getData()));
        var emittedAt = Timestamp.from(Instant.ofEpochMilli(record.getEmittedAt()));
        csvPrinter.printRecord(uuid, jsonData, emittedAt);
      }
    } finally {
      if (writer != null) {
        writer.close();
      }
    }
  }

  protected JsonNode formatData(JsonNode data) {
    return data;
  }

  @Override
  public String truncateTableQuery(JdbcDatabase database, String schemaName, String tableName) {
    return String.format("TRUNCATE TABLE %s.%s;\n", schemaName, tableName);
  }

  @Override
  public String copyTableQuery(JdbcDatabase database, String schemaName, String srcTableName, String dstTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s;\n", schemaName, dstTableName, schemaName, srcTableName);
  }

  @Override
  public void executeTransaction(JdbcDatabase database, List<String> queries) throws Exception {
    final StringBuilder appendedQueries = new StringBuilder();
    appendedQueries.append("BEGIN;\n");
    for (String query : queries) {
      appendedQueries.append(query);
    }
    appendedQueries.append("COMMIT;");
    database.execute(appendedQueries.toString());
  }

  @Override
  public void dropTableIfExists(JdbcDatabase database, String schemaName, String tableName) throws SQLException {
    database.execute(dropTableIfExistsQuery(schemaName, tableName));
  }

  private String dropTableIfExistsQuery(String schemaName, String tableName) {
    return String.format("DROP TABLE IF EXISTS %s.%s;\n", schemaName, tableName);
  }

  @Override
  public boolean isSchemaRequired() {
    return true;
  }

  @Override
  public boolean isValidData(JsonNode data) {
    return true;
  }

  @Override
  public final void insertRecords(JdbcDatabase database,
                                  List<AirbyteRecordMessage> records,
                                  String schemaName,
                                  String tableName)
      throws Exception {
    records.forEach(airbyteRecordMessage -> getDataAdapter().adapt(airbyteRecordMessage.getData()));
    insertRecordsInternal(database, records, schemaName, tableName);
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
