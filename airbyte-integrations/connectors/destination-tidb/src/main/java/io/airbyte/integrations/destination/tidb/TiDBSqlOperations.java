/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.StandardNameTransformer;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;

@SuppressFBWarnings(
    value = {"SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE"},
    justification = "There is little chance of SQL injection. There is also little need for statement reuse. The basic statement is more readable than the prepared statement.")
public class TiDBSqlOperations extends JdbcSqlOperations {

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    database.executeWithinTransaction(queries);
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
        tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
        writeBatchToFile(tmpFile, records);
        String filePath = "'" + tmpFile.getAbsolutePath() + "'";
        String query = String.format(
            "LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s FIELDS TERMINATED BY ',' ENCLOSED BY '\"' ESCAPED BY '' LINES TERMINATED BY '\\r\\n'",
            filePath, schemaName, tmpTableName);

        try (final Statement stmt = connection.createStatement()) {
          stmt.execute(query);
        }

      } catch (IOException e) {
        throw new SQLException(e);
      } catch (Exception e) {
        throw new RuntimeException(e);
      } finally {
        try {
          if (tmpFile != null) {
            Files.delete(tmpFile.toPath());
          }
        } catch (final IOException e) {
          throw new RuntimeException(e);
        }
      }
    });
  }

  @Override
  public boolean isSchemaRequired() {
    return false;
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR(256) PRIMARY KEY,\n"
            + "%s JSON,\n"
            + "%s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6)\n"
            + ");\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    // TiDB use database instead of schema.
    database.execute(String.format("CREATE DATABASE IF NOT EXISTS %s;\n", schemaName));
  }

  @Override
  protected JsonNode formatData(JsonNode data) {
    return StandardNameTransformer.formatJsonPath(data);
  }

}
