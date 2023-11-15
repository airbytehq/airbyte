/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.CustomSqlType;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.DatabaseMetaData;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.SQLType;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Optional;
import java.util.UUID;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
public class JdbcDestinationHandler implements DestinationHandler<TableDefinition> {
  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcDestinationHandler.class);

  private final String databaseName;
  private final JdbcDatabase jdbcDatabase;

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
    return false;
  }

  @Override
  public Optional<Instant> getMinTimestampForSync(final StreamId id) throws Exception {
    return Optional.empty();
  }

  @Override
  public void execute(final String sql) throws Exception {
    if (sql == null || sql.isEmpty()) {
      return;
    }
    final UUID queryId = UUID.randomUUID();
    LOGGER.info("Executing sql {}: {}", queryId, sql);
    final long startTime = System.currentTimeMillis();

    try {
      jdbcDatabase.execute(sql);
    } catch (final SQLException e) {
      LOGGER.error("Sql {} failed", queryId, e);
      throw e;
    }

    LOGGER.info("Sql {} completed in {} ms", queryId, System.currentTimeMillis() - startTime);
  }

  public static Optional<TableDefinition> findExistingTable(
                                                            final JdbcDatabase jdbcDatabase,
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
