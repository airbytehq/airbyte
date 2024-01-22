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
import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.commons.json.Jsons;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;

@SuppressFBWarnings(
        value = {"SQL_NONCONSTANT_STRING_PASSED_TO_EXECUTE"},
        justification = "There is little chance of SQL injection. There is also little need for statement reuse. The basic statement is more readable than the prepared statement.")
public class MySQLSqlOperations extends JdbcSqlOperations {

    Logger LOGGER = LoggerFactory.getLogger(MySQLSqlOperations.class);

//    private boolean isLocalFileEnabled = false;

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

        LOGGER.info("[WorkMagic] insertRecordsInternal tableName=%s, records.size=%s".formatted(tmpTableName, records.size()));

        // hack wm_tenant_id
        String wmTenantId = "0";
        if (database instanceof DefaultJdbcDatabase jdbcDatabase) {
            wmTenantId = jdbcDatabase.getWmTenantId();
        }
        for (final PartialAirbyteMessage record : records) {
            // TODO we only need to do this is formatData is overridden. If not, we can just do jsonData =
            // record.getSerialized()
            var data = Jsons.deserializeExact(record.getSerialized());
            if (data != null && data.isObject()) {
                ObjectNode dataObjectNode = (ObjectNode) data;
                dataObjectNode.set("wm_tenant_id", Jsons.jsonNode(wmTenantId));
            }
            record.setSerialized(Jsons.serialize(data));
        }

        replaceIntoWithPk(database, records, schemaName, tmpTableName);
//        verifyLocalFileEnabled(database);
//        try {
//            final File tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
//
//            loadDataIntoTable(database, records, schemaName, tmpTableName, tmpFile);
//
//            Files.delete(tmpFile.toPath());
//        } catch (final IOException e) {
//            throw new SQLException(e);
//        }
    }

    @Override
    protected void insertRecordsInternalV2(final JdbcDatabase database,
                                           final List<PartialAirbyteMessage> records,
                                           final String schemaName,
                                           final String tableName)
            throws Exception {
        throw new UnsupportedOperationException("mysql does not yet support DV2");
    }

//    @Override
//    protected void writeBatchToFile(final File tmpFile, final List<PartialAirbyteMessage> records) throws Exception {
//        try (final PrintWriter writer = new PrintWriter(tmpFile, StandardCharsets.UTF_8);
//             final CSVPrinter csvPrinter = new CSVPrinter(writer, CSVFormat.MYSQL.withEscape(null).withNullString(null))) {
//            for (final PartialAirbyteMessage record : records) {
//                var data = formatData(Jsons.deserializeExact(record.getSerialized()));
//                var streamDesc = record.getState().getStream().getStreamDescriptor();
//                var catalog = record.getCatalog().getStreams().stream().filter(x -> streamDesc.getName().equals(x.getStream().getName()) && streamDesc.getNamespace().equals(x.getStream().getNamespace())).findFirst();
//                var pk = new AtomicReference<String>(UUID.randomUUID().toString());
//                catalog.ifPresent(c -> {
//                    var pkValue = c.getPrimaryKey().stream().flatMap(List::stream)
//                            .map(p -> data.get(p).asText()).collect(Collectors.joining("|"));
//                    pk.set(pkValue);
//                });
//                // TODO we only need to do this is formatData is overridden. If not, we can just do jsonData =
//                // record.getSerialized()
//                final var jsonData = Jsons.serialize(data);
//                final var extractedAt = Timestamp.from(Instant.ofEpochMilli(record.getRecord().getEmittedAt()));
//                if (TypingAndDedupingFlag.isDestinationV2()) {
//                    csvPrinter.printRecord(pk.get(), jsonData, extractedAt, null);
//                } else {
//                    csvPrinter.printRecord(pk.get(), jsonData, extractedAt);
//                }
//            }
//        }
//    }

    private void replaceIntoWithPk(final JdbcDatabase database,
                                   final List<PartialAirbyteMessage> records,
                                   final String schemaName,
                                   final String tableName) throws SQLException {
        List<List<Object>> rows = new ArrayList<>();
        for (final PartialAirbyteMessage record : records) {
            var data = formatData(Jsons.deserializeExact(record.getSerialized()));
            var catalog = record.getCatalog().getStreams().stream()
                    .filter(x -> record.getRecord().getStream().equals(x.getStream().getName()))
                    .findFirst();
            var pk = new AtomicReference<>("fallback_" + UUID.randomUUID().toString());
            catalog.ifPresent(c -> {
                var pkValue = c.getPrimaryKey().stream().flatMap(List::stream).filter(StringUtils::isNotBlank)
                        .map(p -> data.get(p).asText()).collect(Collectors.joining("|"));
                if (StringUtils.isBlank(pkValue)) {
                    pkValue = c.getCursorField().stream().filter(StringUtils::isNotBlank)
                            .map(p -> data.get(p).asText()).collect(Collectors.joining("|"));
                }
                if (StringUtils.isNotBlank(pkValue)) {
                    pk.set(pkValue);
                }
            });
            final Long wmTenantId = Long.parseLong(data.get("wm_tenant_id").asText());
            final String jsonData = Jsons.serialize(data);
            final Timestamp extractedAt = Timestamp.from(Instant.ofEpochMilli(record.getRecord().getEmittedAt()));
            rows.add(List.of(wmTenantId, pk.get(), jsonData, extractedAt));
        }
        // LOGGER.info("+++++++++++rows: %s".formatted(Jsons.serialize(rows)));
        final String queryPrefix = String.format(
                "REPLACE INTO %s.%s (%s, %s, %s, %s) VALUES ",
                schemaName, tableName, "wm_tenant_id", JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT);

        // 构建带有占位符的 SQL 语句
        String placeholders = "(?, ?, ?, ?)";
        List<String> placeholdersList = new ArrayList<>();
        for (int i = 0; i < rows.size(); i++) {
            placeholdersList.add(placeholders);
        }
        String query = queryPrefix + String.join(", ", placeholdersList);

        database.execute(connection -> {
            try (final PreparedStatement stmt = connection.prepareStatement(query)) {
                int index = 1;
                for (List<Object> row : rows) {
                    stmt.setLong(index++, (Long) row.get(0)); // wm_tenant_id
                    stmt.setString(index++, row.get(1).toString()); // pk
                    stmt.setString(index++, row.get(2).toString()); // jsonData
                    stmt.setTimestamp(index++, (Timestamp) row.get(3)); // extractedAt
                }
                // LOGGER.info("+++++++++++sql: %s".formatted(stmt.toString()));
                var results = stmt.execute();
                LOGGER.info("[WorkMagic]  stmt.execute results=%s".formatted(Jsons.serialize(results)));
            } catch (final SQLException e) {
                throw new RuntimeException("Error executing query: " + query, e);
            }
        });
    }

//    private void loadDataIntoTable(final JdbcDatabase database,
//                                   final List<PartialAirbyteMessage> records,
//                                   final String schemaName,
//                                   final String tmpTableName,
//                                   final File tmpFile)
//            throws SQLException {
//        database.execute(connection -> {
//            try {
//                writeBatchToFile(tmpFile, records);
//
//                final String absoluteFile = "'" + tmpFile.getAbsolutePath() + "'";
//
//                final String query = String.format(
//                        "LOAD DATA LOCAL INFILE %s INTO TABLE %s.%s",
//                        absoluteFile, schemaName, tmpTableName);
//
//                try (final Statement stmt = connection.createStatement()) {
//                    stmt.execute(query);
//                }
//            } catch (final Exception e) {
//                throw new RuntimeException(e);
//            }
//        });
//    }

    @Override
    protected JsonNode formatData(final JsonNode data) {
        return StandardNameTransformer.formatJsonPath(data);
    }

//    void verifyLocalFileEnabled(final JdbcDatabase database) throws SQLException {
//        final boolean localFileEnabled = isLocalFileEnabled || checkIfLocalFileIsEnabled(database);
//        if (!localFileEnabled) {
//            tryEnableLocalFile(database);
//        }
//        isLocalFileEnabled = true;
//    }
//
//    private void tryEnableLocalFile(final JdbcDatabase database) throws SQLException {
//        database.execute(connection -> {
//            try (final Statement statement = connection.createStatement()) {
//                statement.execute("set global local_infile=true");
//            } catch (final Exception e) {
//                throw new RuntimeException(
//                        "The DB user provided to airbyte was unable to switch on the local_infile attribute on the MySQL server. As an admin user, you will need to run \"SET GLOBAL local_infile = true\" before syncing data with Airbyte.",
//                        e);
//            }
//        });
//    }

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

//    private boolean checkIfLocalFileIsEnabled(final JdbcDatabase database) throws SQLException {
//        final List<String> localFiles = database.queryStrings(
//                connection -> connection.createStatement().executeQuery("SHOW GLOBAL VARIABLES LIKE 'local_infile'"),
//                resultSet -> resultSet.getString("Value"));
//        return localFiles.get(0).equalsIgnoreCase("on");
//    }

    @Override
    public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
        // MySQL requires byte information with VARCHAR. Since we are using uuid as value for the column,
        // 256 is enough
        return String.format(
                "CREATE TABLE IF NOT EXISTS %s.%s ( \n"
                        + "wm_tenant_id BIGINT,\n"
                        + "%s VARCHAR(256),\n"
                        + "%s JSON,\n"
                        + "%s TIMESTAMP(6) DEFAULT CURRENT_TIMESTAMP(6),\n"
                        + "PRIMARY KEY (wm_tenant_id, %s)"
                        + ");\n",
                schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_ID, JavaBaseConstants.COLUMN_NAME_DATA, JavaBaseConstants.COLUMN_NAME_EMITTED_AT, JavaBaseConstants.COLUMN_NAME_AB_ID);
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
