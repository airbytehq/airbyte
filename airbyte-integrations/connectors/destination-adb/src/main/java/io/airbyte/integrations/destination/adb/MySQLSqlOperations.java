/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.adb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import edu.umd.cs.findbugs.annotations.SuppressFBWarnings;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.base.TypingAndDedupingFlag;
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.commons.json.Jsons;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVPrinter;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.UUID;

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

  @Override
  protected void insertRecordsInternalV2(final JdbcDatabase database,
                                         final List<PartialAirbyteMessage> records,
                                         final String schemaName,
                                         final String tableName)
      throws Exception {
    throw new UnsupportedOperationException("mysql does not yet support DV2");
  }

  @Override
  protected void writeBatchToFile(final File tmpFile, final List<PartialAirbyteMessage> records) throws Exception {
    writeBatchToFile(tmpFile, records, "0");
  }

  protected void writeBatchToFile(final File tmpFile, final List<PartialAirbyteMessage> records, String wmTenantId) throws Exception {
    try (final PrintWriter writer = new PrintWriter(tmpFile, StandardCharsets.UTF_8);
         final CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.MYSQL.withEscape(null).withNullString(null))) {
      for (final PartialAirbyteMessage record : records) {
        final var uuid = UUID.randomUUID().toString();
        // TODO we only need to do this is formatData is overridden. If not, we can just do jsonData =
        // record.getSerialized()
        var data = Jsons.deserializeExact(record.getSerialized());
        if (data != null && data.isObject()) {
          ObjectNode dataObjectNode = (ObjectNode) data;
          dataObjectNode.set("wm_tenant_id", Jsons.jsonNode(wmTenantId));
        }
        var jsonData = Jsons.serialize(formatData(data));

        final var extractedAt = Timestamp.from(Instant.ofEpochMilli(record.getRecord().getEmittedAt()));
        if (TypingAndDedupingFlag.isDestinationV2()) {
          csvPrinter.printRecord(uuid, jsonData, extractedAt, null);
        } else {
          csvPrinter.printRecord(uuid, jsonData, extractedAt);
        }
      }
    }
  }

  private void loadDataIntoTable(final JdbcDatabase database,
                                 final List<PartialAirbyteMessage> records,
                                 final String schemaName,
                                 final String tmpTableName,
                                 final File tmpFile)
      throws SQLException {
    database.execute(connection -> {
      try {
        // hack wm_tenant_id
        String wm_tenant_id = "0";
        if (database instanceof DefaultJdbcDatabase jdbcDatabase) {
          wm_tenant_id = jdbcDatabase.getWmTenantId();
        }

        writeBatchToFile(tmpFile, records, wm_tenant_id);

        final String absoluteFile = "'" + tmpFile.getAbsolutePath() + "'";

        final String query = String.format(
            "LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s",
            absoluteFile, schemaName, tmpTableName);

        try (final Statement stmt = connection.createStatement()) {
//          LOGGER.info("loadDataIntoTable sql:%s".formatted(query));
//          String content = new String(Files.readAllBytes(Paths.get(tmpFile.getAbsolutePath())), StandardCharsets.UTF_8);
//          LOGGER.info("loadDataIntoTable sql file content:%s".formatted(content));
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
    return new VersionCompatibility(version, version >= 5.6);
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
