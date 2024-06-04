/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.table;

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;

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
                                    final List<PartialAirbyteMessage> records,
                                    final String schemaName,
                                    final String tmpTableName)
      throws SQLException {
    throw new UnsupportedOperationException("Mysql requires V2");
  }

  @Override
  protected void insertRecordsInternalV2(final JdbcDatabase database,
                                         final List<PartialAirbyteMessage> records,
                                         final String schemaName,
                                         final String tableName)
      throws Exception {
    if (records.isEmpty()) {
      return;
    }

    verifyLocalFileEnabled(database);
    try {
      final File tmpFile = Files.createTempFile(tableName + "-", ".tmp").toFile();

      loadDataIntoTable(
          database,
          records,
          schemaName,
          tableName,
          tmpFile,
          COLUMN_NAME_AB_RAW_ID,
          COLUMN_NAME_DATA,
          COLUMN_NAME_AB_EXTRACTED_AT,
          COLUMN_NAME_AB_LOADED_AT,
          COLUMN_NAME_AB_META);
      Files.delete(tmpFile.toPath());
    } catch (final IOException e) {
      throw new SQLException(e);
    }
  }

  private void loadDataIntoTable(final JdbcDatabase database,
                                 final List<PartialAirbyteMessage> records,
                                 final String schemaName,
                                 final String tmpTableName,
                                 final File tmpFile,
                                 final String... columnNames)
      throws SQLException {
    database.execute(connection -> {
      try {
        writeBatchToFile(tmpFile, records);

        final String absoluteFile = "'" + tmpFile.getAbsolutePath() + "'";

        /*
         * We want to generate a query like:
         *
         * LOAD DATA LOCAL INFILE '/a/b/c' INTO TABLE foo.bar FIELDS TERMINATED BY ',' ENCLOSED BY
         * '"' ESCAPED BY '\"' LINES TERMINATED BY '\r\n' (@c0, @c1, @c2, @c3, @c4) SET _airybte_raw_id =
         * NULLIF(@c0, ''), _airbyte_data = NULLIF(@c1, ''), _airbyte_extracted_at = NULLIF(@c2, ''),
         * _airbyte_loaded_at = NULLIF(@c3, ''), _airbyte_meta = NULLIF(@c4, '')
         *
         * This is to avoid weird default values (e.g. 0000-00-00 00:00:00) when the value should be NULL.
         */

        final String colVarDecls = "("
            + IntStream.range(0, columnNames.length).mapToObj(i -> "@c" + i).collect(Collectors.joining(","))
            + ")";
        final String colAssignments = IntStream.range(0, columnNames.length)
            .mapToObj(i -> columnNames[i] + " = NULLIF(@c" + i + ", '')")
            .collect(Collectors.joining(","));

        final String query = String.format(
            """
            LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s
            FIELDS TERMINATED BY ',' ENCLOSED BY '"' ESCAPED BY '\\"'
            LINES TERMINATED BY '\\r\\n'
            %s
            SET
            %s
            """,
            absoluteFile,
            schemaName,
            tmpTableName,
            colVarDecls,
            colAssignments);
        try (final Statement stmt = connection.createStatement()) {
          stmt.execute(query);
        }
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
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
  public void createTableIfNotExists(
                                     JdbcDatabase database,
                                     String schemaName,
                                     String tableName)
      throws SQLException {
    super.createTableIfNotExists(database, schemaName, tableName);

    // mysql doesn't have a "create index if not exists" method, and throws an error
    // if you create an index that already exists.
    // So we can't just override postCreateTableQueries.
    // Instead, we manually query for index existence and create the index if needed.
    // jdbc metadata is... weirdly painful to use for finding indexes:
    // (getIndexInfo requires isUnique / isApproximate, which sounds like an easy thing to get wrong),
    // and jooq doesn't support `show` queries,
    // so manually build the query string. We can at least use jooq to render the table name.
    String tableId = DSL.using(SQLDialect.MYSQL).render(table(name(schemaName, tableName)));
    // This query returns a list of columns in the index, or empty list if the index does not exist.
    boolean unloadedExtractedAtIndexNotExists =
        database.queryJsons("show index from " + tableId + " where key_name='unloaded_extracted_at'").isEmpty();
    if (unloadedExtractedAtIndexNotExists) {
      database.execute(DSL.using(SQLDialect.MYSQL).createIndex("unloaded_extracted_at")
          .on(
              table(name(schemaName, tableName)),
              field(name(COLUMN_NAME_AB_LOADED_AT)),
              field(name(COLUMN_NAME_AB_EXTRACTED_AT)))
          .getSQL());
    }
    boolean extractedAtIndexNotExists = database.queryJsons("show index from " + tableId + " where key_name='extracted_at'").isEmpty();
    if (extractedAtIndexNotExists) {
      database.execute(DSL.using(SQLDialect.MYSQL).createIndex("extracted_at")
          .on(
              table(name(schemaName, tableName)),
              field(name(COLUMN_NAME_AB_EXTRACTED_AT)))
          .getSQL());
    }
  }

  @Override
  protected String createTableQueryV1(String schemaName, String tableName) {
    throw new UnsupportedOperationException("Mysql requires V2");
  }

  @Override
  protected String createTableQueryV2(String schemaName, String tableName) {
    // MySQL requires byte information with VARCHAR. Since we are using uuid as value for the column,
    // 256 is enough
    return String.format(
        """
        CREATE TABLE IF NOT EXISTS %s.%s (\s
        %s VARCHAR(256) PRIMARY KEY,
        %s JSON,
        %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
        %s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),
        %s JSON
        );
        """,
        schemaName,
        tableName,
        JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
        JavaBaseConstants.COLUMN_NAME_DATA,
        JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
        JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT,
        JavaBaseConstants.COLUMN_NAME_AB_META);
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
