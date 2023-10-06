/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.SQLException;
import java.util.LinkedHashMap;
import java.util.Optional;
import java.util.UUID;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeDestinationHandler implements DestinationHandler<SnowflakeTableDefinition> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDestinationHandler.class);
  public static final String EXCEPTION_COMMON_PREFIX = "JavaScript execution error: Uncaught Execution of multiple statements failed on statement";

  private final String databaseName;
  private final JdbcDatabase database;

  public SnowflakeDestinationHandler(final String databaseName, final JdbcDatabase database) {
    this.databaseName = databaseName;
    this.database = database;
  }

  @Override
  public Optional<SnowflakeTableDefinition> findExistingTable(final StreamId id) throws SQLException {
    // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC translates
    // VARIANT as VARCHAR
    final LinkedHashMap<String, String> columns = database.queryJsons(
        """
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        ORDER BY ordinal_position;
        """,
        databaseName.toUpperCase(),
        id.finalNamespace().toUpperCase(),
        id.finalName().toUpperCase()).stream()
        .collect(LinkedHashMap::new,
            (map, row) -> map.put(row.get("COLUMN_NAME").asText(), row.get("DATA_TYPE").asText()),
            LinkedHashMap::putAll);
    // TODO query for indexes/partitioning/etc

    if (columns.isEmpty()) {
      return Optional.empty();
    } else {
      return Optional.of(new SnowflakeTableDefinition(columns));
    }
  }

  @Override
  public boolean isFinalTableEmpty(final StreamId id) throws SQLException {
    final int rowCount = database.queryInt(
        """
        SELECT row_count
        FROM information_schema.tables
        WHERE table_catalog = ?
          AND table_schema = ?
          AND table_name = ?
        """,
        databaseName.toUpperCase(),
        id.finalNamespace().toUpperCase(),
        id.finalName().toUpperCase());
    return rowCount == 0;
  }

  @Override
  public void execute(final String sql) throws Exception {
    if ("".equals(sql)) {
      return;
    }
    final UUID queryId = UUID.randomUUID();
    LOGGER.info("Executing sql {}: {}", queryId, sql);
    final long startTime = System.currentTimeMillis();

    try {
      database.execute(sql);
    } catch (final SnowflakeSQLException e) {
      LOGGER.error("Sql {} failed", queryId, e);
      // Snowflake SQL exceptions by default may not be super helpful, so we try to extract the relevant
      // part of the message.
      final String trimmedMessage;
      if (e.getMessage().startsWith(EXCEPTION_COMMON_PREFIX)) {
        // The first line is a pretty generic message, so just remove it
        trimmedMessage = e.getMessage().substring(e.getMessage().indexOf("\n") + 1);
      } else {
        trimmedMessage = e.getMessage();
      }
      throw new RuntimeException(trimmedMessage, e);
    }

    LOGGER.info("Sql {} completed in {} ms", queryId, System.currentTimeMillis() - startTime);
  }

}
