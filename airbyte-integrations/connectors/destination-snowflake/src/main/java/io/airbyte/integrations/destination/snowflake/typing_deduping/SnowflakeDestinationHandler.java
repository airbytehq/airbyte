/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.Array;
import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialState;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStateImpl;
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

  public static LinkedHashMap<String, LinkedHashMap<String, TableDefinition>> findExistingTables(final JdbcDatabase database,
                                                                                                 final String databaseName,
                                                                                                 final List<StreamId> streamIds)
      throws SQLException {
    final LinkedHashMap<String, LinkedHashMap<String, TableDefinition>> existingTables = new LinkedHashMap<>();
    final String paramHolder = String.join(",", Collections.nCopies(streamIds.size(), "?"));
    // convert list stream to array
    final String[] namespaces = streamIds.stream().map(StreamId::finalNamespace).toArray(String[]::new);
    final String[] names = streamIds.stream().map(StreamId::finalName).toArray(String[]::new);
    final String query = """
                         SELECT table_schema, table_name, column_name, data_type, is_nullable
                         FROM information_schema.columns
                         WHERE table_catalog = ?
                           AND table_schema IN (%s)
                           AND table_name IN (%s)
                         ORDER BY table_schema, table_name, ordinal_position;
                         """.formatted(paramHolder, paramHolder);
    final String[] bindValues = new String[streamIds.size() * 2 + 1];
    bindValues[0] = databaseName.toUpperCase();
    System.arraycopy(namespaces, 0, bindValues, 1, namespaces.length);
    System.arraycopy(names, 0, bindValues, namespaces.length + 1, names.length);
    final List<JsonNode> results = database.queryJsons(query, bindValues);
    for (final JsonNode result : results) {
      final String tableSchema = result.get("TABLE_SCHEMA").asText();
      final String tableName = result.get("TABLE_NAME").asText();
      final String columnName = result.get("COLUMN_NAME").asText();
      final String dataType = result.get("DATA_TYPE").asText();
      final String isNullable = result.get("IS_NULLABLE").asText();
      final TableDefinition tableDefinition = existingTables
          .computeIfAbsent(tableSchema, k -> new LinkedHashMap<>())
          .computeIfAbsent(tableName, k -> new TableDefinition(new LinkedHashMap<>()));
      tableDefinition.columns().put(columnName, new ColumnDefinition(columnName, dataType, 0, fromIsNullableIsoString(isNullable)));
    }
    return existingTables;
  }

  private LinkedHashMap<String, LinkedHashMap<String, Integer>> getFinalTableRowCount(final List<StreamId> streamIds) throws SQLException {
    final LinkedHashMap<String, LinkedHashMap<String, Integer>> tableRowCounts = new LinkedHashMap<>();
    final String paramHolder = String.join(",", Collections.nCopies(streamIds.size(), "?"));
    // convert list stream to array
    final String[] namespaces = streamIds.stream().map(StreamId::finalNamespace).toArray(String[]::new);
    final String[] names = streamIds.stream().map(StreamId::finalName).toArray(String[]::new);
    final String query = """
                         SELECT table_schema, table_name, row_count
                         FROM information_schema.tables
                         WHERE table_catalog = ?
                           AND table_schema IN (%s)
                           AND table_name IN (%s)
                         """.formatted(paramHolder, paramHolder);
    final String[] bindValues = new String[streamIds.size() * 2 + 1];
    bindValues[0] = databaseName.toUpperCase();
    System.arraycopy(namespaces, 0, bindValues, 1, namespaces.length);
    System.arraycopy(names, 0, bindValues, namespaces.length + 1, names.length);
    final List<JsonNode> results = database.queryJsons(query, bindValues);
    for (final JsonNode result : results) {
      final String tableSchema = result.get("TABLE_SCHEMA").asText();
      final String tableName = result.get("TABLE_NAME").asText();
      final int rowCount = result.get("ROW_COUNT").asInt();
      tableRowCounts.computeIfAbsent(tableSchema, k -> new LinkedHashMap<>()).put(tableName, rowCount);
    }
    return tableRowCounts;
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

  private boolean isAirbyteRawIdColumnMatch(final TableDefinition existingTable) {
    final String abRawIdColumnName = COLUMN_NAME_AB_RAW_ID.toUpperCase();
    return existingTable.columns().containsKey(abRawIdColumnName) &&
        toJdbcTypeName(AirbyteProtocolType.STRING).equals(existingTable.columns().get(abRawIdColumnName).type());
  }

  private boolean isAirbyteExtractedAtColumnMatch(final TableDefinition existingTable) {
    final String abExtractedAtColumnName = COLUMN_NAME_AB_EXTRACTED_AT.toUpperCase();
    return existingTable.columns().containsKey(abExtractedAtColumnName) &&
        toJdbcTypeName(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE).equals(existingTable.columns().get(abExtractedAtColumnName).type());
  }

  private boolean isAirbyteMetaColumnMatch(TableDefinition existingTable) {
    final String abMetaColumnName = COLUMN_NAME_AB_META.toUpperCase();
    return existingTable.columns().containsKey(abMetaColumnName) &&
        "VARIANT".equals(existingTable.columns().get(abMetaColumnName).type());
  }

  protected boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    final Set<String> pks = getPks(stream);
    // This is same as JdbcDestinationHandler#existingSchemaMatchesStreamConfig with upper case
    // conversion.
    // TODO: Unify this using name transformer or something.
    if (!isAirbyteRawIdColumnMatch(existingTable) ||
        !isAirbyteExtractedAtColumnMatch(existingTable) ||
        !isAirbyteMetaColumnMatch(existingTable)) {
      // Missing AB meta columns from final table, we need them to do proper T+D so trigger soft-reset
      return false;
    }
    final LinkedHashMap<String, String> intendedColumns = stream.columns().entrySet().stream()
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey().name(), toJdbcTypeName(column.getValue())),
            LinkedHashMap::putAll);

    // Filter out Meta columns since they don't exist in stream config.
    final LinkedHashMap<String, String> actualColumns = existingTable.columns().entrySet().stream()
        .filter(column -> V2_FINAL_TABLE_METADATA_COLUMNS.stream().map(String::toUpperCase)
            .noneMatch(airbyteColumnName -> airbyteColumnName.equals(column.getKey())))
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey(), column.getValue().type()),
            LinkedHashMap::putAll);
    // soft-resetting https://github.com/airbytehq/airbyte/pull/31082
    @SuppressWarnings("deprecation")
    final boolean hasPksWithNonNullConstraint = existingTable.columns().entrySet().stream()
        .anyMatch(c -> pks.contains(c.getKey()) && !c.getValue().isNullable());

    return !hasPksWithNonNullConstraint
        && actualColumns.equals(intendedColumns);

  }

  @Override
  public List<DestinationInitialState> gatherInitialState(List<StreamConfig> streamConfigs) throws Exception {
    List<StreamId> streamIds = streamConfigs.stream().map(StreamConfig::id).toList();
    final LinkedHashMap<String, LinkedHashMap<String, TableDefinition>> existingTables = findExistingTables(database, databaseName, streamIds);
    final LinkedHashMap<String, LinkedHashMap<String, Integer>> tableRowCounts = getFinalTableRowCount(streamIds);
    return streamConfigs.stream().map(streamConfig -> {
      try {
        final String namespace = streamConfig.id().finalNamespace().toUpperCase();
        final String name = streamConfig.id().finalName().toUpperCase();
        boolean isSchemaMismatch = false;
        boolean isFinalTableEmpty = true;
        boolean isFinalTablePresent = existingTables.containsKey(namespace) && existingTables.get(namespace).containsKey(name);
        boolean hasRowCount = tableRowCounts.containsKey(namespace) && tableRowCounts.get(namespace).containsKey(name);
        if (isFinalTablePresent) {
          final TableDefinition existingTable = existingTables.get(namespace).get(name);
          isSchemaMismatch = !existingSchemaMatchesStreamConfig(streamConfig, existingTable);
          isFinalTableEmpty = hasRowCount && tableRowCounts.get(namespace).get(name) == 0;
        }
        final InitialRawTableState initialRawTableState = getInitialRawTableState(streamConfig.id());
        return new DestinationInitialStateImpl(streamConfig, isFinalTablePresent, initialRawTableState, isSchemaMismatch, isFinalTableEmpty);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    }).collect(Collectors.toList());
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
