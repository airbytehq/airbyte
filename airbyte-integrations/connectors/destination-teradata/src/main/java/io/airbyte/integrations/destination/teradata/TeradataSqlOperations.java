/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.commons.json.Jsons;
import org.apache.commons.lang3.StringUtils;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;

public class TeradataSqlOperations extends JdbcSqlOperations {

    private static final Logger LOGGER = LoggerFactory.getLogger(TeradataSqlOperations.class);


    // TODO: implement V2 insert. Use MySQLSqlOperations as inspiration
    @Override
    protected void insertRecordsInternalV2(@NotNull JdbcDatabase jdbcDatabase,
                                           @NotNull List<PartialAirbyteMessage> records,
                                           @Nullable String schemaName,
                                           @Nullable String tableName) throws SQLException {
        insertRecordsInternal(jdbcDatabase, records, schemaName, tableName,
                COLUMN_NAME_AB_RAW_ID,
                COLUMN_NAME_DATA,
                COLUMN_NAME_AB_EXTRACTED_AT,
                COLUMN_NAME_AB_LOADED_AT,
                COLUMN_NAME_AB_META);
    }

    private void insertRecordsInternal(final JdbcDatabase database,
                                       final List<PartialAirbyteMessage> records,
                                       final String schemaName,
                                       final String tmpTableName,
                                       final String... columnNames)
            throws SQLException {
        if (records.isEmpty()) {
            return;
        }
        // Explicitly passing column order to avoid order mismatches between CREATE TABLE and INSERT statement
        final String orderedColumnNames = StringUtils.join(columnNames, ", ");
        database.execute(connection -> {
            PreparedStatement statement = null;
            try {
                final var sql = String.format("INSERT INTO %s.%s (%s) VALUES (%s)",
                        schemaName, tmpTableName, orderedColumnNames, StringUtils.repeat("?", ", ", columnNames.length));
                statement = connection.prepareStatement(sql);
                for (PartialAirbyteMessage record : records) {
                    var uuid = UUID.randomUUID().toString();

                    var jsonData = record.getSerialized();
                    String airbyteMeta;
                    if (record.getRecord().getMeta() == null) {
                        airbyteMeta = "{\"changes\":[]}";
                    } else {
                        airbyteMeta = Jsons.serialize(record.getRecord().getMeta());
                    }
                    var extractedAt =
                            Timestamp.from(Instant.ofEpochMilli(record.getRecord().getEmittedAt()));

                    statement.setObject(1, uuid);
                    statement.setObject(2, jsonData);
                    statement.setTimestamp(3, extractedAt);
                    statement.setTimestamp(4, null);
                    statement.setObject(5, airbyteMeta);
                    statement.addBatch();
                }
                statement.executeBatch();
            } catch (final Exception e) {
                throw new RuntimeException(e);
            } finally {
                if (statement != null) {
                    try {
                        statement.close();
                    } catch (final SQLException e) {
                        throw new RuntimeException(e);
                    }
                }
            }
        });
    }

    @Override
    protected void insertRecordsInternal(@NotNull JdbcDatabase jdbcDatabase,
                                         @NotNull List<PartialAirbyteMessage> records,
                                         @Nullable String schemaName,
                                         @Nullable String tableName) throws Exception {

        if (records.isEmpty()) {
            return;
        }
        final String insertQueryComponent = String.format("INSERT INTO %s.%s (%s, %s, %s) VALUES (?, ?, ?)", schemaName, tableName,
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT);
        jdbcDatabase.execute(con -> {
            try {

                final PreparedStatement pstmt = con.prepareStatement(insertQueryComponent);
                for (final PartialAirbyteMessage record : records) {

                    final String uuid = UUID.randomUUID().toString();
                    final String jsonData = record.getSerialized();
                    final Timestamp emittedAt = Timestamp.from(Instant.ofEpochMilli(record.getRecord().getEmittedAt()));
                    pstmt.setString(1, uuid);
                    pstmt.setString(2, jsonData);
                    pstmt.setTimestamp(3, emittedAt);
                    pstmt.addBatch();

                }

                pstmt.executeBatch();
            } catch (final SQLException se) {
                for (SQLException ex = se; ex != null; ex = ex.getNextException()) {
                    LOGGER.info(ex.getMessage());
                }
                AirbyteTraceMessageUtility.emitTransientErrorTrace(se,
                        "Connector failed while inserting records to staging table");
                throw new RuntimeException(se);
            } catch (final Exception e) {
                AirbyteTraceMessageUtility.emitTransientErrorTrace(e,
                        "Connector failed while inserting records to staging table");
                throw new RuntimeException(e);
            }
        });
    }

    @Override
    public void createSchemaIfNotExists(JdbcDatabase database, String schemaName) {
        try {
            Set<String> schemaSet = getSchemaSet();
            schemaSet.forEach(System.out::println);
            if (!schemaSet.contains(schemaName) && !isSchemaExists(database, schemaName)) {
                database.execute(String.format("CREATE DATABASE \"%s\" AS PERMANENT = 120e6, SPOOL = 120e6;", schemaName));
                schemaSet.add(schemaName);
            }
        } catch (final Exception e) {
            if (e.getMessage().contains("already exists")) {
                LOGGER.warn("Database " + schemaName + " already exists.");
            } else {
                AirbyteTraceMessageUtility.emitTransientErrorTrace(e, "Connector failed while creating schema ");
                throw new RuntimeException(e);
            }
        }
    }

    @Override
    public void createTableIfNotExists(final JdbcDatabase database, final String schemaName, final String tableName) {
        try {
            database.execute(createTableQuery(database, schemaName, tableName));
        } catch (final SQLException e) {
            if (e.getMessage().contains("already exists")) {
                LOGGER.warn("Table " + schemaName + "." + tableName + " already exists.");
            } else {
                AirbyteTraceMessageUtility.emitTransientErrorTrace(e, "Connector failed while creating table ");
                throw new RuntimeException(e);
            }
        }
    }

    @Override
    public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
        return String.format(
                "CREATE MULTISET TABLE %s.%s ( %s VARCHAR(256), %s JSON, %s TIMESTAMP(6), %s TIMESTAMP(6), %s JSON) NO PRIMARY INDEX",
                schemaName, tableName, JavaBaseConstants.COLUMN_NAME_AB_RAW_ID, JavaBaseConstants.COLUMN_NAME_DATA,
                JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT, JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT, JavaBaseConstants.COLUMN_NAME_AB_META);
    }

    @Override
    public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName) {
        try {
            database.execute(dropTableIfExistsQueryInternal(schemaName, tableName));
        } catch (final Exception e) {
            AirbyteTraceMessageUtility.emitTransientErrorTrace(e,
                    "Connector failed while inserting records to staging table");
            throw new RuntimeException(e);
        }

    }

    @Override
    public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
        try {
            return String.format("DELETE %s.%s ALL;\n", schemaName, tableName);
        } catch (final Exception e) {
            AirbyteTraceMessageUtility.emitTransientErrorTrace(e,
                    "Connector failed while truncating table " + schemaName + "." + tableName);
        }
        return "";
    }

    private String dropTableIfExistsQueryInternal(final String schemaName, final String tableName) {
        try {
            return String.format("DROP TABLE  %s.%s;\n", schemaName, tableName);
        } catch (final Exception e) {
            AirbyteTraceMessageUtility.emitTransientErrorTrace(e,
                    "Connector failed while dropping table " + schemaName + "." + tableName);
        }
        return "";
    }

    @Override
    public void executeTransaction(final JdbcDatabase database, final List<String> queries) {
        final StringBuilder appendedQueries = new StringBuilder();
        try {
            for (final String query : queries) {
                appendedQueries.append(query);
            }
            database.execute(appendedQueries.toString());
        } catch (final SQLException e) {
            AirbyteTraceMessageUtility.emitTransientErrorTrace(e,
                    "Connector failed while executing queries : " + appendedQueries);
        }
    }
}
