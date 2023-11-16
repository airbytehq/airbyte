/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.apache.commons.text.StringSubstitutor;
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
    final LinkedHashMap<String, SnowflakeColumnDefinition> columns = database.queryJsons(
        """
        SELECT column_name, data_type, is_nullable
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
            (map, row) -> map.put(
                row.get("COLUMN_NAME").asText(),
                new SnowflakeColumnDefinition(row.get("DATA_TYPE").asText(), fromSnowflakeBoolean(row.get("IS_NULLABLE").asText()))),
            LinkedHashMap::putAll);
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
  public Optional<Instant> getMinTimestampForSync(final StreamId id) throws Exception {
    final ResultSet tables = database.getMetaData().getTables(
        databaseName,
        id.rawNamespace(),
        id.rawName(),
        null);
    if (!tables.next()) {
      return Optional.empty();
    }
    // Snowflake timestamps have nanosecond precision, so decrement by 1ns
    // And use two explicit queries because COALESCE doesn't short-circuit.
    // This first query tries to find the oldest raw record with loaded_at = NULL
    Optional<String> minUnloadedTimestamp = Optional.ofNullable(database.queryStrings(
        conn -> conn.createStatement().executeQuery(new StringSubstitutor(Map.of(
            "raw_table", id.rawTableId(SnowflakeSqlGenerator.QUOTE))).replace(
                """
                SELECT to_varchar(
                  TIMESTAMPADD(NANOSECOND, -1, MIN("_airbyte_extracted_at")),
                  'YYYY-MM-DDTHH24:MI:SS.FF9TZH:TZM'
                ) AS MIN_TIMESTAMP
                FROM ${raw_table}
                WHERE "_airbyte_loaded_at" IS NULL
                """)),
        // The query will always return exactly one record, so use .get(0)
        record -> record.getString("MIN_TIMESTAMP")).get(0));
    if (minUnloadedTimestamp.isEmpty()) {
      // If there are no unloaded raw records, then we can safely skip all existing raw records.
      // This second query just finds the newest raw record.
      minUnloadedTimestamp = Optional.ofNullable(database.queryStrings(
          conn -> conn.createStatement().executeQuery(new StringSubstitutor(Map.of(
              "raw_table", id.rawTableId(SnowflakeSqlGenerator.QUOTE))).replace(
                  """
                  SELECT to_varchar(
                    MAX("_airbyte_extracted_at"),
                    'YYYY-MM-DDTHH24:MI:SS.FF9TZH:TZM'
                  ) AS MIN_TIMESTAMP
                  FROM ${raw_table}
                  """)),
          record -> record.getString("MIN_TIMESTAMP")).get(0));
    }
    return minUnloadedTimestamp.map(Instant::parse);
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

  /**
   * In snowflake information_schema tables, booleans return "YES" and "NO", which DataBind doesn't
   * know how to use
   */
  private boolean fromSnowflakeBoolean(final String input) {
    return input.equalsIgnoreCase("yes");
  }

}
