/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.DatabaseMetaData;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLType;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
public class JdbcDestinationHandler implements DestinationHandler<TableDefinition> {

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcDestinationHandler.class);

  protected final String databaseName;
  protected final JdbcDatabase jdbcDatabase;

  public JdbcDestinationHandler(final String databaseName,
                                final JdbcDatabase jdbcDatabase) {
    this.databaseName = databaseName;
    this.jdbcDatabase = jdbcDatabase;
  }

  @Override
  public Optional<TableDefinition> findExistingTable(final StreamId id) throws Exception {
    return findExistingTable(jdbcDatabase, databaseName, id.finalNamespace(), id.finalName());
  }

  @Override
  public boolean isFinalTableEmpty(final StreamId id) throws Exception {
    final int rowCount = jdbcDatabase.queryInt(
        """
        SELECT row_count
        FROM information_schema.tables
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        """,
        databaseName,
        id.finalNamespace(),
        id.finalName());
    return rowCount == 0;
  }

  @Override
  public InitialRawTableState getInitialRawTableState(final StreamId id) throws Exception {
    final ResultSet tables = jdbcDatabase.getMetaData().getTables(
        databaseName,
        id.rawNamespace(),
        id.rawName(),
        null);
    if (!tables.next()) {
      // There's no raw table at all. Therefore there are no unprocessed raw records, and this sync
      // should not filter raw records by timestamp.
      return new InitialRawTableState(false, Optional.empty());
    }
    // And use two explicit queries because COALESCE might not short-circuit evaluation.
    // This first query tries to find the oldest raw record with loaded_at = NULL.
    // Unsafe query requires us to explicitly close the Stream, which is inconvenient,
    // but it's also the only method in the JdbcDatabase interface to return non-string/int types
    try (final Stream<Timestamp> timestampStream = jdbcDatabase.unsafeQuery(
        conn -> conn.prepareStatement(
            DSL.select(DSL.field("MIN(_airbyte_extracted_at)").as("min_timestamp"))
                .from(DSL.name(id.rawNamespace(), id.rawName()))
                .where(DSL.condition("_airbyte_loaded_at IS NULL"))
                .getSQL()),
        record -> record.getTimestamp("min_timestamp"))) {
      // Filter for nonNull values in case the query returned NULL (i.e. no unloaded records).
      final Optional<Timestamp> minUnloadedTimestamp = timestampStream.filter(Objects::nonNull).findFirst();
      if (minUnloadedTimestamp.isPresent()) {
        // Decrement by 1 second since timestamp precision varies between databases.
        final Optional<Instant> ts = minUnloadedTimestamp
            .map(Timestamp::toInstant)
            .map(i -> i.minus(1, ChronoUnit.SECONDS));
        return new InitialRawTableState(true, ts);
      }
    }
    // If there are no unloaded raw records, then we can safely skip all existing raw records.
    // This second query just finds the newest raw record.
    try (final Stream<Timestamp> timestampStream = jdbcDatabase.unsafeQuery(
        conn -> conn.prepareStatement(
            DSL.select(DSL.field("MAX(_airbyte_extracted_at)").as("min_timestamp"))
                .from(DSL.name(id.rawNamespace(), id.rawName()))
                .getSQL()),
        record -> record.getTimestamp("min_timestamp"))) {
      // Filter for nonNull values in case the query returned NULL (i.e. no raw records at all).
      final Optional<Timestamp> minUnloadedTimestamp = timestampStream.filter(Objects::nonNull).findFirst();
      return new InitialRawTableState(false, minUnloadedTimestamp.map(Timestamp::toInstant));
    }
  }

  @Override
  public void execute(final Sql sql) throws Exception {
    final List<List<String>> transactions = sql.transactions();
    final UUID queryId = UUID.randomUUID();
    for (final List<String> transaction : transactions) {
      final UUID transactionId = UUID.randomUUID();
      LOGGER.info("Executing sql {}-{}: {}", queryId, transactionId, String.join("\n", transaction));
      final long startTime = System.currentTimeMillis();

      try {
        jdbcDatabase.executeWithinTransaction(transaction);
      } catch (final SQLException e) {
        LOGGER.error("Sql {}-{} failed", queryId, transactionId, e);
        throw e;
      }

      LOGGER.info("Sql {}-{} completed in {} ms", queryId, transactionId, System.currentTimeMillis() - startTime);
    }
  }

  public static Optional<TableDefinition> findExistingTable(final JdbcDatabase jdbcDatabase,
                                                            final String databaseName,
                                                            final String schemaName,
                                                            final String tableName)
      throws SQLException {
    final DatabaseMetaData metaData = jdbcDatabase.getMetaData();
    // TODO: normalize namespace and finalName strings to quoted-lowercase (as needed. Snowflake
    // requires uppercase)
    final LinkedHashMap<String, ColumnDefinition> columnDefinitions = new LinkedHashMap<>();
    try (final ResultSet columns = metaData.getColumns(databaseName, schemaName, tableName, null)) {
      while (columns.next()) {
        final String columnName = columns.getString("COLUMN_NAME");
        final String typeName = columns.getString("TYPE_NAME");
        final int columnSize = columns.getInt("COLUMN_SIZE");
        final int datatype = columns.getInt("DATA_TYPE");
        SQLType sqlType;
        try {
          sqlType = JDBCType.valueOf(datatype);
        } catch (final IllegalArgumentException e) {
          // Unknown jdbcType convert to customSqlType
          LOGGER.warn("Unrecognized JDBCType {}; falling back to UNKNOWN", datatype, e);
          sqlType = new CustomSqlType("Unknown", "Unknown", datatype);
        }
        columnDefinitions.put(columnName, new ColumnDefinition(columnName, typeName, sqlType, columnSize));
      }
    }
    // Guard to fail fast
    if (columnDefinitions.isEmpty()) {
      return Optional.empty();
    }

    return Optional.of(new TableDefinition(columnDefinitions));
  }

}
