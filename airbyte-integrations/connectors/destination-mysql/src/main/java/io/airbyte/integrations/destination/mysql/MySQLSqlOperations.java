/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

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
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;

@SuppressFBWarnings(
    value = {"SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE"},
    justification = "There is little chance of SQL injection. There is also little need for statement reuse. The basic statement is more readable than the prepared statement.")
public class MySQLSqlOperations extends JdbcSqlOperations {

  private boolean isLocalFileEnabled = false;

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

    verifyLocalFileEnabled(database);
    try {
      final File tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();

      loadDataIntoTable(database, records, schemaName, tmpTableName, tmpFile);

      Files.delete(tmpFile.toPath());
    } catch (final IOException e) {
      throw new SQLException(e);
    }
  }

  private void loadDataIntoTable(final JdbcDatabase database,
                                 final List<AirbyteRecordMessage> records,
                                 final String schemaName,
                                 final String tmpTableName,
                                 final File tmpFile)
      throws SQLException {
    database.execute(connection -> {
      try {
        writeBatchToFile(tmpFile, records);

        final String absoluteFile = "'" + tmpFile.getAbsolutePath() + "'";

        final String query = String.format(
            "LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s FIELDS TERMINATED BY ',' ENCLOSED BY '\"' ESCAPED BY '\\\"' LINES TERMINATED BY '\\r\\n'",
            absoluteFile, schemaName, tmpTableName);

        try (final Statement stmt = connection.createStatement()) {
          stmt.execute(query);
        }
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  protected JsonNode formatData(final JsonNode data) {
    return StandardNameTransformer.formatJsonPath(data);
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
            "The DB user provided to airbyte was unable to switch on the local_infile attribute on the MySQL server. As an admin user, you will need to run \"SET GLOBAL local_infile = true\" before syncing data with Airbyte.",
            e);
      }
    });
  }

  private double getVersion(final JdbcDatabase database) throws SQLException {
    final List<String> versions = database.queryStrings(
        connection -> connection.createStatement().executeQuery("select version()"),
        resultSet -> resultSet.getString("version()"));
    return Double.parseDouble(versions.get(0).substring(0, 3));
  }

  VersionCompatibility isCompatibleVersion(final JdbcDatabase database) throws SQLException {
    final double version = getVersion(database);
    return new VersionCompatibility(version, version >= 5.7);
  }

  @Override
  public boolean isSchemaRequired() {
    return false;
  }

  private boolean checkIfLocalFileIsEnabled(final JdbcDatabase database) throws SQLException {
    final List<String> localFiles = database.queryStrings(
        connection -> connection.createStatement().executeQuery("SHOW GLOBAL VARIABLES LIKE 'local_infile'"),
        resultSet -> resultSet.getString("Value"));
    return localFiles.get(0).equalsIgnoreCase("on");
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    // MySQL requires byte information with VARCHAR. Since we are using uuid as value for the column,
    // 256 is enough
    return String.format(
        "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
            + "%s VARCHAR(256) PRIMARY KEY,\n"
            + "%s JSON,\n"
            + "%s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6)\n"
            + ");\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  public static class VersionCompatibility {

    private final double version;
    private final boolean isCompatible;

    public VersionCompatibility(final double version, final boolean isCompatible) {
      this.version = version;
      this.isCompatible = isCompatible;
    }

    public double getVersion() {
      return version;
    }

    public boolean isCompatible() {
      return isCompatible;
    }

  }

}
