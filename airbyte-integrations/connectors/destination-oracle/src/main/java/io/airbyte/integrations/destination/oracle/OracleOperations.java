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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.SqlOperations;
import io.airbyte.integrations.destination.jdbc.SqlOperationsUtils;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.function.Supplier;

public class OracleOperations implements SqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(OracleOperations.class);

  private String tablespace;

  public OracleOperations(String tablespace)
  {
    this.tablespace = tablespace;
  }

  @Override
  public void createSchemaIfNotExists(JdbcDatabase database, String schemaName) throws Exception {
    final String query = String.format("declare userExists integer; begin select count(*) into userExists from dba_users where upper(username) = upper('%s'); " +
          "if (userExists = 0) then " +
          "execute immediate 'create user %s identified by %s'; " +
          "execute immediate 'alter user %s quota unlimited on %s'; " +
          "end if; end;",
        schemaName, schemaName, schemaName, schemaName, tablespace);
    database.execute(query);
  }

  @Override
  public void createTableIfNotExists(JdbcDatabase database, String schemaName, String tableName) throws Exception {
    LOGGER.error(String.format("Create table if not exists: %s.%s", schemaName, tableName));
    int count = database.query(c -> {
        PreparedStatement statement = c.prepareStatement("select count(*) \n from user_tables\n where upper(table_name) = upper(?)");
        statement.setString(1, tableName);
        return statement;
      },
      rs -> rs.getInt(1)
    ).findFirst().get();
    if (count == 0)
    {
      database.execute(createTableQuery(schemaName, tableName));
    }
  }

  @Override
  public String createTableQuery(String schemaName, String tableName) {
    return String.format(
                    "CREATE TABLE %s.%s ( \n"
                    + "%s VARCHAR(64) PRIMARY KEY,\n"
                    + "%s NCLOB,\n"
                    + "%s TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\n"
                    + ")",
            schemaName, tableName,
            JavaBaseConstants.COLUMN_NAME_AB_ID.substring(1), JavaBaseConstants.COLUMN_NAME_DATA.substring(1), JavaBaseConstants.COLUMN_NAME_EMITTED_AT.substring(1),
            JavaBaseConstants.COLUMN_NAME_DATA.substring(1));
  }

  /*
  @Override
  public String createTableQuery(String schemaName, String tableName) {
    return String.format(
        "declare c int; \n"
            + "begin\n select count(*) into c\n from user_tables\n where upper(table_name) = upper('%s');\n"
            + "if c = 1 then\n" +
            " execute immediate '\n"
            + "CREATE TABLE %s.%s ( \n"
            + "%s VARCHAR(64) PRIMARY KEY,\n"
            + "%s VARCHAR(MAX),\n"
            + "%s TIMESTAMP WITH TIME ZONE DEFAULT SYSDATETIMEOFFSET()\n"
            + ");';\n"

            + "execute immediate '\n"
            + "GRANT SELECT, INSERT on %s.%s to user \n"
            + ";';\n"

            + "execute immediate '\n"
            + "GRANT SELECT, INSERT on NONEXISTENT to user \n"
            + ";';\n"

            + "end if; end;",
        tableName, schemaName, tableName,
        JavaBaseConstants.COLUMN_NAME_AB_ID.substring(1), JavaBaseConstants.COLUMN_NAME_DATA.substring(1), JavaBaseConstants.COLUMN_NAME_EMITTED_AT.substring(1),
        schemaName, tableName);
  }
*/

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
  public String truncateTableQuery(String schemaName, String tableName) {
    return String.format("TRUNCATE TABLE %s.%s\n", schemaName, tableName);
  }


  @Override
  public void insertRecords(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tempTableName)
          throws Exception {

    final String insertQueryComponent = String.format(
            "INSERT INTO %s.%s (%s, %s, %s) VALUES\n",
            schemaName,
            tempTableName,
            JavaBaseConstants.COLUMN_NAME_AB_ID.substring(1),
            JavaBaseConstants.COLUMN_NAME_DATA.substring(1),
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT.substring(1));
    final String recordQueryComponent = "(?, ?, ?),\n";
    for (AirbyteRecordMessage r : records) {
      List<AirbyteRecordMessage> message = Arrays.asList(new AirbyteRecordMessage[]{r});
      SqlOperationsUtils.insertRawRecordsInSingleQueryNoSem(insertQueryComponent, recordQueryComponent, database, message);
      int count = database.query(
              c -> c.prepareStatement(String.format("select count(*) \n from %s.%s", schemaName, tempTableName)),
              rs -> rs.getInt(1)
      ).findFirst().get();
      LOGGER.error(String.format("%d records in %s.%s after insert.", count, schemaName, tempTableName));
    }
    database.execute("commit");
    //SqlOperationsUtils.insertRawRecordsInSingleQuery(insertQueryComponent, recordQueryComponent, database, records);
  }

  /*
  @Override
  public void insertRecords(JdbcDatabase database, List<AirbyteRecordMessage> records, String schemaName, String tempTableName)
      throws Exception {

    LOGGER.error(String.format("Inserting records: count %d", records.size()));

    final String tableName = String.format("%s.%s", schemaName, tempTableName);
    final String columns = String.format("(%s, %s, %s)",
            JavaBaseConstants.COLUMN_NAME_AB_ID.substring(1),
            JavaBaseConstants.COLUMN_NAME_DATA.substring(1),
            JavaBaseConstants.COLUMN_NAME_EMITTED_AT.substring(1));
    final String recordQueryComponent = "(?, ?, ?)\n";
    insertRawRecordsInSingleQuery(tableName, columns, recordQueryComponent, database, records, UUID::randomUUID);
  }

  static void insertRawRecordsInSingleQuery(String tableName,
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
*/

  @Override
  public String copyTableQuery(String schemaName, String sourceTableName, String destinationTableName) {
    return String.format("INSERT INTO %s.%s SELECT * FROM %s.%s\n", schemaName, destinationTableName, schemaName, sourceTableName);
  }

  @Override
  public void executeTransaction(JdbcDatabase database, List<String> queries) throws Exception {
    database.execute("BEGIN TRAN;\n" + String.join("\n", queries) + "\nCOMMIT TRAN");
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
