/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mariadb_columnstore;

import com.vdurmont.semver4j.Semver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class MariadbColumnstoreSqlOperations extends JdbcSqlOperations {

  private final String MINIMUM_VERSION = "5.5.3";
  Pattern VERSION_PATTERN = Pattern.compile("^(\\d+\\.\\d+\\.\\d+)-MariaDB");
  private boolean isLocalFileEnabled = false;

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

    File tmpFile = null;
    Exception primaryException = null;
    try {
      tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
      writeBatchToFile(tmpFile, records);

      final String query = String.format(
          "LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s FIELDS TERMINATED BY ',' ENCLOSED BY '\"' ESCAPED BY '\\\"' LINES TERMINATED BY '\\r\\n'",
          String.format("'%s'", tmpFile.getAbsolutePath()), schemaName, tmpTableName);

      database.execute(query);
    } catch (final Exception e) {
      primaryException = e;
      throw new RuntimeException(primaryException);
    } finally {
      try {
        if (tmpFile != null) {
          Files.delete(tmpFile.toPath());
        }
      } catch (final IOException e) {
        if (primaryException != null)
          e.addSuppressed(primaryException);
        throw new RuntimeException(e);
      }
    }
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    database.execute(connection -> {
      try (final Statement stmt = connection.createStatement()) {
        stmt.addBatch("BEGIN;");
        for (final String query : queries) {
          stmt.addBatch(query);
        }
        stmt.addBatch("COMMIT;");
        stmt.executeBatch();
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
            + "%s VARCHAR(256),\n"
            + "%s LONGTEXT,\n"
            + "%s TIMESTAMP\n"
            + ") engine=columnstore;\n",
        schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
  }

  VersionCompatibility isCompatibleVersion(final JdbcDatabase database) throws SQLException {
    final Semver version = getVersion(database);
    return new VersionCompatibility(version, version.isGreaterThanOrEqualTo(MINIMUM_VERSION));
  }

  private Semver getVersion(final JdbcDatabase database) throws SQLException {
    final List<String> versions = database.queryStrings(
        connection -> connection.createStatement().executeQuery("SELECT version()"),
        resultSet -> resultSet.getString("version()"));

    final Matcher matcher = VERSION_PATTERN.matcher(versions.get(0));
    if (matcher.find()) {
      return new Semver(matcher.group(1));
    } else {
      throw new RuntimeException(String.format("Unexpected version string: %s\nExpected version format is X.X.X-MariaDB", versions.get(0)));
    }
  }

  void verifyLocalFileEnabled(final JdbcDatabase database) throws SQLException {
    final boolean localFileEnabled = isLocalFileEnabled || checkIfLocalFileIsEnabled(database);
    if (!localFileEnabled) {
      tryEnableLocalFile(database);
    }
    isLocalFileEnabled = true;
  }

  private boolean checkIfLocalFileIsEnabled(final JdbcDatabase database) throws SQLException {
    final List<String> localFiles = database.queryStrings(
        connection -> connection.createStatement().executeQuery("SHOW GLOBAL VARIABLES LIKE 'local_infile'"),
        resultSet -> resultSet.getString("Value"));
    return localFiles.get(0).equalsIgnoreCase("on");
  }

  private void tryEnableLocalFile(final JdbcDatabase database) throws SQLException {
    database.execute(connection -> {
      try (final Statement statement = connection.createStatement()) {
        statement.execute("SET GLOBAL local_infile=true");
      } catch (final Exception e) {
        throw new RuntimeException(
            "The DB user provided to airbyte was unable to switch on the local_infile attribute on the MariaDB server. As an admin user, you will need to run \"SET GLOBAL local_infile = true\" before syncing data with Airbyte.",
            e);
      }
    });
  }

  public static class VersionCompatibility {

    private final Semver version;
    private final boolean isCompatible;

    public VersionCompatibility(final Semver version, final boolean isCompatible) {
      this.version = version;
      this.isCompatible = isCompatible;
    }

    public Semver getVersion() {
      return version;
    }

    public boolean isCompatible() {
      return isCompatible;
    }

  }

}
