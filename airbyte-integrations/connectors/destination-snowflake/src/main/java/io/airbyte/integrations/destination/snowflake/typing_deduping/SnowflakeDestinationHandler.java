/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;

import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialState;
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableState;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.Union;
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import net.snowflake.client.jdbc.SnowflakeSQLException;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SnowflakeDestinationHandler extends JdbcDestinationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(SnowflakeDestinationHandler.class);
  public static final String EXCEPTION_COMMON_PREFIX = "JavaScript execution error: Uncaught Execution of multiple statements failed on statement";

  private final String databaseName;
  private final JdbcDatabase database;

  public SnowflakeDestinationHandler(final String databaseName, final JdbcDatabase database) {
    super(databaseName, database);
    this.databaseName = databaseName;
    this.database = database;
  }

  public Optional<TableDefinition> findExistingTable(final StreamId id) throws SQLException {
    // The obvious database.getMetaData().getColumns() solution doesn't work, because JDBC translates
    // VARIANT as VARCHAR
    final LinkedHashMap<String, ColumnDefinition> columns = database.queryJsons(
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
                     new ColumnDefinition(
                         row.get("COLUMN_NAME").asText(),
                         row.get("DATA_TYPE").asText(),
                         0, //unused
                         fromIsNullableIsoString(row.get("IS_NULLABLE").asText()))),
                 LinkedHashMap::putAll);
    if (columns.isEmpty()) {
      return Optional.empty();
    } else {
      return Optional.of(new TableDefinition(columns));
    }
  }

  private boolean isFinalTableEmpty(final StreamId id) throws SQLException {
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


  public InitialRawTableState getInitialRawTableState(final StreamId id) throws Exception {
    final ResultSet tables = database.getMetaData().getTables(
        databaseName,
        id.rawNamespace(),
        id.rawName(),
        null);
    if (!tables.next()) {
      return new InitialRawTableState(false, Optional.empty());
    }
    // Snowflake timestamps have nanosecond precision, so decrement by 1ns
    // And use two explicit queries because COALESCE doesn't short-circuit.
    // This first query tries to find the oldest raw record with loaded_at = NULL
    final Optional<String> minUnloadedTimestamp = Optional.ofNullable(database.queryStrings(
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
    if (minUnloadedTimestamp.isPresent()) {
      return new InitialRawTableState(true, minUnloadedTimestamp.map(Instant::parse));
    }

    // If there are no unloaded raw records, then we can safely skip all existing raw records.
    // This second query just finds the newest raw record.
    final Optional<String> maxTimestamp = Optional.ofNullable(database.queryStrings(
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
    return new InitialRawTableState(false, maxTimestamp.map(Instant::parse));
  }

  @Override
  public void execute(final Sql sql) throws Exception {
    final List<String> transactions = sql.asSqlStrings("BEGIN TRANSACTION", "COMMIT");
    final UUID queryId = UUID.randomUUID();
    for (final String transaction : transactions) {
      final UUID transactionId = UUID.randomUUID();
      LOGGER.debug("Executing sql {}-{}: {}", queryId, transactionId, transaction);
      final long startTime = System.currentTimeMillis();

      try {
        database.execute(transaction);
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

      LOGGER.debug("Sql {}-{} completed in {} ms", queryId, transactionId, System.currentTimeMillis() - startTime);
    }
  }


  private Set<String> getPks(final StreamConfig stream) {
    return stream.primaryKey() != null ? stream.primaryKey().stream().map(ColumnId::name).collect(Collectors.toSet()) : Collections.emptySet();
  }

  @Override
  protected boolean isAirbyteMetaColumnMatch(TableDefinition existingTable) {
    return existingTable.columns().containsKey(COLUMN_NAME_AB_META) &&
        "VARIANT".equals(existingTable.columns().get(COLUMN_NAME_AB_META).type());
  }

  protected boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    final Set<String> pks = getPks(stream);
    // soft-resetting https://github.com/airbytehq/airbyte/pull/31082
    @SuppressWarnings("deprecation") final boolean hasPksWithNonNullConstraint = existingTable.columns().entrySet().stream()
        .anyMatch(c -> pks.contains(c.getKey()) && !c.getValue().isNullable());

    return !hasPksWithNonNullConstraint
        && super.existingSchemaMatchesStreamConfig(stream, existingTable);

  }

  @Override
  public List<DestinationInitialState> gatherInitialState(List<StreamConfig> streamConfigs) throws Exception {
    return null;
  }

  @Override
  protected String toJdbcTypeName(AirbyteType airbyteType) {
    if (airbyteType instanceof final AirbyteProtocolType p) {
      return toJdbcTypeName(p);
    }

    return switch (airbyteType.getTypeName()) {
      case Struct.TYPE -> "OBJECT";
      case Array.TYPE -> "ARRAY";
      case UnsupportedOneOf.TYPE -> "VARIANT";
      case Union.TYPE -> toJdbcTypeName(((Union) airbyteType).chooseType());
      default -> throw new IllegalArgumentException("Unrecognized type: " + airbyteType.getTypeName());
    };
  }

  private String toJdbcTypeName(final AirbyteProtocolType airbyteProtocolType) {
    return switch (airbyteProtocolType) {
      case STRING -> "TEXT";
      case NUMBER -> "FLOAT";
      case INTEGER -> "NUMBER";
      case BOOLEAN -> "BOOLEAN";
      case TIMESTAMP_WITH_TIMEZONE -> "TIMESTAMP_TZ";
      case TIMESTAMP_WITHOUT_TIMEZONE -> "TIMESTAMP_NTZ";
      // If you change this - also change the logic in extractAndCast
      case TIME_WITH_TIMEZONE -> "TEXT";
      case TIME_WITHOUT_TIMEZONE -> "TIME";
      case DATE -> "DATE";
      case UNKNOWN -> "VARIANT";
    };
  }
}
