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

package io.airbyte.integrations.destination.oracle;

import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class OracleOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleOperations.class);

  private String tablespace;

  public OracleOperations(String tablespace) {
    this.tablespace = tablespace;
  }

  @Override
  public void createSchemaIfNotExists(JdbcDatabase database, String schemaName) throws Exception {
    if (database.queryInt("select count(*) from all_users where upper(username) = upper(?)", schemaName) == 0) {
      LOGGER.warn("Schema " + schemaName + " is not found! Trying to create a new one.");
      final String query = String.format("create user %s identified by %s quota unlimited on %s",
          schemaName, schemaName, tablespace);
      database.execute(query);
    }
  }

  @Override
  public void createTableIfNotExists(JdbcDatabase database, String schemaName, String tableName) throws Exception {
    try {
      if (!tableExists(database, schemaName, tableName)) {
        database.execute(createTableQuery(database, schemaName, tableName));
      }
    } catch (Exception e) {
      LOGGER.error("Error while creating table.", e);
      throw e;
    }
  }

  @Override
  public String createTableQuery(JdbcDatabase database, String schemaName, String tableName) {
    return String.format(
        "CREATE TABLE %s.%s ( \n"
            + "%s VARCHAR(64) PRIMARY KEY,\n"
            + "%s NCLOB,\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
            + ")",
        schemaName, tableName,
        OracleDestination.COLUMN_NAME_AB_ID, OracleDestination.COLUMN_NAME_DATA, OracleDestination.COLUMN_NAME_EMITTED_AT,
        OracleDestination.COLUMN_NAME_DATA);
  }

  private boolean tableExists(JdbcDatabase database, String schemaName, String tableName) throws Exception {
    Integer count = database.queryInt("select count(*) \n from all_tables\n where upper(owner) = upper(?) and upper(table_name) = upper(?)",
        schemaName, tableName);
    return count == 1;
  }

  @Override
  public void dropTableIfExists(JdbcDatabase database, String schemaName, String tableName) throws Exception {
    if (tableExists(database, schemaName, tableName)) {
      try {
        final String query = String.format("DROP TABLE %s.%s", schemaName, tableName);
        database.execute(query);
      } catch (Exception e) {
        LOGGER.error(String.format("Error dropping table %s.%s", schemaName, tableName), e);
        throw e;
      }
    }
  }

  @Override
  public String truncateTableQuery(JdbcDatabase database, String schemaName, String tableName) {
    return String.format("DELETE FROM %s.%s\n", schemaName, tableName);
  }

  @Override
  public void insertRecords(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tempTableName)
      throws Exception {
    final String tableName = String.format("%s.%s", schemaName, tempTableName);
    final String columns = String.format("(%s, %s, %s)",
        OracleDestination.COLUMN_NAME_AB_ID, OracleDestination.COLUMN_NAME_DATA, OracleDestination.COLUMN_NAME_EMITTED_AT);
    final String recordQueryComponent = "(?, ?, ?)\n";
    insertRawRecordsInSingleQuery(tableName, columns, recordQueryComponent, database, records, UUID::randomUUID);
  }

  // Adapted from SqlUtils.insertRawRecordsInSingleQuery to meet some needs specific to Oracle syntax
  private static void insertRawRecordsInSingleQuery(String tableName,
                                                    String columns,
                                                    String recordQueryComponent,
                                                    JdbcDatabase jdbcDatabase,
                                                    List<AirbyteRecordMessage> records,
                                                    Supplier<UUID> uuidSupplier)
      throws SQLException {
    if (records.isEmpty()) {
      return;
    }

    jdbcDatabase.execute(connection -> {

      // Strategy: We want to use PreparedStatement because it handles binding values to the SQL query
      // (e.g. handling formatting timestamps). A PreparedStatement statement is created by supplying the
      // full SQL string at creation time. Then subsequently specifying which values are bound to the
      // string. Thus there will be two loops below.
      // 1) Loop over records to build the full string.
      // 2) Loop over the records and bind the appropriate values to the string.
      //
      // The "SELECT 1 FROM DUAL" at the end is a formality to satisfy the needs of the Oracle syntax.
      // (see https://stackoverflow.com/a/93724 for details)
      final StringBuilder sql = new StringBuilder("INSERT ALL ");
      records.forEach(r -> sql.append(String.format("INTO %s %s VALUES %s", tableName, columns, recordQueryComponent)));
      sql.append(" SELECT 1 FROM DUAL");
      final String query = sql.toString();

      try (final PreparedStatement statement = connection.prepareStatement(query)) {
        // second loop: bind values to the SQL string.
        int i = 1;
        for (final AirbyteRecordMessage message : records) {
          // 1-indexed
          statement.setString(i, uuidSupplier.get().toString());
          statement.setString(i + 1, Jsons.serialize(message.getData()));
          statement.setTimestamp(i + 2, Timestamp.from(Instant.ofEpochMilli(message.getEmittedAt())));
          i += 3;
        }

        statement.execute();
      }
    });
  }

  @Override
  public String copyTableQuery(JdbcDatabase database, String schemaName, String sourceTableName, String destinationTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s\n", schemaName, destinationTableName, schemaName, sourceTableName);
  }

  @Override
  public void executeTransaction(JdbcDatabase database, List<String> queries) throws Exception {
    String SQL = "BEGIN\n COMMIT;\n" + String.join(";\n", queries) + "; \nCOMMIT; \nEND;";
    database.execute(SQL);
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
