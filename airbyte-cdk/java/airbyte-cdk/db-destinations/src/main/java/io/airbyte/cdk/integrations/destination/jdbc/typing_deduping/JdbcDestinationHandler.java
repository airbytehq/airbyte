/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_META;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_AB_RAW_ID;
import static io.airbyte.cdk.integrations.base.JavaBaseConstants.V2_FINAL_TABLE_METADATA_COLUMNS;
import static java.util.stream.Collectors.toMap;
import static org.jooq.impl.DSL.exists;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.name;
import static org.jooq.impl.DSL.quotedName;
import static org.jooq.impl.DSL.selectOne;
import static org.jooq.impl.DSL.table;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.integrations.destination.jdbc.ColumnDefinition;
import io.airbyte.cdk.integrations.destination.jdbc.TableDefinition;
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil;
import io.airbyte.commons.concurrency.CompletableFutures;
import io.airbyte.commons.exceptions.SQLRuntimeException;
import io.airbyte.commons.functional.Either;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationHandler;
import io.airbyte.integrations.base.destination.typing_deduping.DestinationInitialStatus;
import io.airbyte.integrations.base.destination.typing_deduping.InitialRawTableStatus;
import io.airbyte.integrations.base.destination.typing_deduping.Sql;
import io.airbyte.integrations.base.destination.typing_deduping.StreamConfig;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.base.destination.typing_deduping.Struct;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.time.temporal.ChronoUnit;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionStage;
import java.util.stream.Stream;
import lombok.extern.slf4j.Slf4j;
import org.jetbrains.annotations.NotNull;
import org.jooq.Condition;
import org.jooq.DSLContext;
import org.jooq.InsertValuesStep4;
import org.jooq.Record;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
public abstract class JdbcDestinationHandler<DestinationState> implements DestinationHandler<DestinationState> {

  private static final Logger LOGGER = LoggerFactory.getLogger(JdbcDestinationHandler.class);
  private static final String DESTINATION_STATE_TABLE_NAME = "_airbyte_destination_state";
  private static final String DESTINATION_STATE_TABLE_COLUMN_NAME = "name";
  private static final String DESTINATION_STATE_TABLE_COLUMN_NAMESPACE = "namespace";
  private static final String DESTINATION_STATE_TABLE_COLUMN_STATE = "destination_state";
  private static final String DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT = "updated_at";

  protected final String databaseName;
  protected final JdbcDatabase jdbcDatabase;
  protected final String rawTableSchemaName;
  private final SQLDialect dialect;

  public JdbcDestinationHandler(final String databaseName,
                                final JdbcDatabase jdbcDatabase,
                                final String rawTableSchemaName,
                                final SQLDialect dialect) {
    this.databaseName = databaseName;
    this.jdbcDatabase = jdbcDatabase;
    this.rawTableSchemaName = rawTableSchemaName;
    this.dialect = dialect;
  }

  protected DSLContext getDslContext() {
    return DSL.using(dialect);
  }

  private Optional<TableDefinition> findExistingTable(final StreamId id) throws Exception {
    return findExistingTable(jdbcDatabase, databaseName, id.finalNamespace(), id.finalName());
  }

  private boolean isFinalTableEmpty(final StreamId id) throws Exception {
    return !jdbcDatabase.queryBoolean(
        getDslContext().select(
            field(exists(
                selectOne()
                    .from(name(id.finalNamespace(), id.finalName()))
                    .limit(1))))
            .getSQL(ParamType.INLINED));
  }

  private InitialRawTableStatus getInitialRawTableState(final StreamId id) throws Exception {
    boolean tableExists = jdbcDatabase.executeMetadataQuery(dbmetadata -> {
      LOGGER.info("Retrieving table from Db metadata: {} {} {}", databaseName, id.rawNamespace(), id.rawName());
      try (final ResultSet table = dbmetadata.getTables(databaseName, id.rawNamespace(), id.rawName(), null)) {
        return table.next();
      } catch (SQLException e) {
        LOGGER.error("Failed to retrieve table info from metadata", e);
        throw new SQLRuntimeException(e);
      }
    });
    if (!tableExists) {
      // There's no raw table at all. Therefore there are no unprocessed raw records, and this sync
      // should not filter raw records by timestamp.
      return new InitialRawTableStatus(false, false, Optional.empty());
    }
    // And use two explicit queries because COALESCE might not short-circuit evaluation.
    // This first query tries to find the oldest raw record with loaded_at = NULL.
    // Unsafe query requires us to explicitly close the Stream, which is inconvenient,
    // but it's also the only method in the JdbcDatabase interface to return non-string/int types
    try (final Stream<Timestamp> timestampStream = jdbcDatabase.unsafeQuery(
        conn -> conn.prepareStatement(
            getDslContext().select(field("MIN(_airbyte_extracted_at)").as("min_timestamp"))
                .from(name(id.rawNamespace(), id.rawName()))
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
        return new InitialRawTableStatus(true, true, ts);
      }
    }
    // If there are no unloaded raw records, then we can safely skip all existing raw records.
    // This second query just finds the newest raw record.
    try (final Stream<Timestamp> timestampStream = jdbcDatabase.unsafeQuery(
        conn -> conn.prepareStatement(
            getDslContext().select(field("MAX(_airbyte_extracted_at)").as("min_timestamp"))
                .from(name(id.rawNamespace(), id.rawName()))
                .getSQL()),
        record -> record.getTimestamp("min_timestamp"))) {
      // Filter for nonNull values in case the query returned NULL (i.e. no raw records at all).
      final Optional<Timestamp> minUnloadedTimestamp = timestampStream.filter(Objects::nonNull).findFirst();
      return new InitialRawTableStatus(true, false, minUnloadedTimestamp.map(Timestamp::toInstant));
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

  @Override
  public List<DestinationInitialStatus<DestinationState>> gatherInitialState(List<StreamConfig> streamConfigs) throws Exception {
    // Use stream n/ns pair because we don't want to build the full StreamId here
    CompletableFuture<Map<AirbyteStreamNameNamespacePair, DestinationState>> destinationStatesFuture = CompletableFuture.supplyAsync(() -> {
      try {
        return getAllDestinationStates();
      } catch (SQLException e) {
        throw new RuntimeException(e);
      }
    });

    final List<CompletionStage<DestinationInitialStatus<DestinationState>>> initialStates = streamConfigs.stream()
        .map(streamConfig -> retrieveState(destinationStatesFuture, streamConfig))
        .toList();
    final List<Either<? extends Exception, DestinationInitialStatus<DestinationState>>> states =
        CompletableFutures.allOf(initialStates).toCompletableFuture().join();
    return ConnectorExceptionUtil.getResultsOrLogAndThrowFirst("Failed to retrieve initial state", states);
  }

  @NotNull
  protected Map<AirbyteStreamNameNamespacePair, DestinationState> getAllDestinationStates() throws SQLException {
    // Guarantee the table exists.
    jdbcDatabase.execute(
        getDslContext().createTableIfNotExists(quotedName(rawTableSchemaName, DESTINATION_STATE_TABLE_NAME))
            .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME), SQLDataType.VARCHAR)
            .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE), SQLDataType.VARCHAR)
            // Just use a string type, even if the destination has a json type.
            // We're never going to query this column in a fancy way - all our processing can happen
            // client-side.
            .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE), SQLDataType.VARCHAR)
            // Add an updated_at field. We don't actually need it yet, but it can't hurt!
            .column(quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT), SQLDataType.TIMESTAMPWITHTIMEZONE)
            .getSQL(ParamType.INLINED));
    // Fetch all records from it. We _could_ filter down to just our streams... but meh. This is small
    // data.
    return jdbcDatabase.queryJsons(
        getDslContext().select(
            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME)),
            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE)),
            field(quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE))).from(quotedName(rawTableSchemaName, DESTINATION_STATE_TABLE_NAME))
            .getSQL())
        .stream().collect(toMap(
            record -> {
              final JsonNode nameNode = record.get(DESTINATION_STATE_TABLE_COLUMN_NAME);
              final JsonNode namespaceNode = record.get(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE);
              return new AirbyteStreamNameNamespacePair(
                  nameNode != null ? nameNode.asText() : null,
                  namespaceNode != null ? namespaceNode.asText() : null);
            },
            record -> toDestinationState(Jsons.deserialize(record.get(DESTINATION_STATE_TABLE_COLUMN_STATE).asText()))));
  }

  private CompletionStage<DestinationInitialStatus<DestinationState>> retrieveState(final CompletableFuture<Map<AirbyteStreamNameNamespacePair, DestinationState>> destinationStatesFuture,
                                                                                    final StreamConfig streamConfig) {
    return destinationStatesFuture.thenApply(destinationStates -> {
      try {
        final Optional<TableDefinition> finalTableDefinition = findExistingTable(streamConfig.id());
        final boolean isSchemaMismatch;
        final boolean isFinalTableEmpty;
        if (finalTableDefinition.isPresent()) {
          isSchemaMismatch = !existingSchemaMatchesStreamConfig(streamConfig, finalTableDefinition.get());
          isFinalTableEmpty = isFinalTableEmpty(streamConfig.id());
        } else {
          // If the final table doesn't exist, then by definition it doesn't have a schema mismatch and has no
          // records.
          isSchemaMismatch = false;
          isFinalTableEmpty = true;
        }
        final InitialRawTableStatus initialRawTableState = getInitialRawTableState(streamConfig.id());
        DestinationState destinationState = destinationStates.getOrDefault(streamConfig.id().asPair(), toDestinationState(Jsons.emptyObject()));
        return new DestinationInitialStatus<>(streamConfig, finalTableDefinition.isPresent(), initialRawTableState,
            isSchemaMismatch, isFinalTableEmpty, destinationState);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

  public static Optional<TableDefinition> findExistingTable(final JdbcDatabase jdbcDatabase,
                                                            final String databaseName,
                                                            final String schemaName,
                                                            final String tableName)
      throws SQLException {
    final LinkedHashMap<String, ColumnDefinition> retrievedColumnDefns = jdbcDatabase.executeMetadataQuery(dbMetadata -> {

      // TODO: normalize namespace and finalName strings to quoted-lowercase (as needed. Snowflake
      // requires uppercase)
      final LinkedHashMap<String, ColumnDefinition> columnDefinitions = new LinkedHashMap<>();
      LOGGER.info("Retrieving existing columns for {}.{}.{}", databaseName, schemaName, tableName);
      try (final ResultSet columns = dbMetadata.getColumns(databaseName, schemaName, tableName, null)) {
        while (columns.next()) {
          final String columnName = columns.getString("COLUMN_NAME");
          final String typeName = columns.getString("TYPE_NAME");
          final int columnSize = columns.getInt("COLUMN_SIZE");
          final String isNullable = columns.getString("IS_NULLABLE");
          columnDefinitions.put(columnName, new ColumnDefinition(columnName, typeName, columnSize, fromIsNullableIsoString(isNullable)));
        }
      } catch (final SQLException e) {
        LOGGER.error("Failed to retrieve column info for {}.{}.{}", databaseName, schemaName, tableName, e);
        throw new SQLRuntimeException(e);
      }
      return columnDefinitions;
    });
    // Guard to fail fast
    if (retrievedColumnDefns.isEmpty()) {
      return Optional.empty();
    }

    return Optional.of(new TableDefinition(retrievedColumnDefns));
  }

  public static boolean fromIsNullableIsoString(final String isNullable) {
    return "YES".equalsIgnoreCase(isNullable);
  }

  private boolean isAirbyteRawIdColumnMatch(final TableDefinition existingTable) {
    return existingTable.columns().containsKey(COLUMN_NAME_AB_RAW_ID) &&
        toJdbcTypeName(AirbyteProtocolType.STRING).equals(existingTable.columns().get(COLUMN_NAME_AB_RAW_ID).type());
  }

  private boolean isAirbyteExtractedAtColumnMatch(final TableDefinition existingTable) {
    return existingTable.columns().containsKey(COLUMN_NAME_AB_EXTRACTED_AT) &&
        toJdbcTypeName(AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE).equals(existingTable.columns().get(COLUMN_NAME_AB_EXTRACTED_AT).type());
  }

  private boolean isAirbyteMetaColumnMatch(final TableDefinition existingTable) {
    return existingTable.columns().containsKey(COLUMN_NAME_AB_META) &&
        toJdbcTypeName(new Struct(new LinkedHashMap<>())).equals(existingTable.columns().get(COLUMN_NAME_AB_META).type());
  }

  protected boolean existingSchemaMatchesStreamConfig(final StreamConfig stream, final TableDefinition existingTable) {
    // Check that the columns match, with special handling for the metadata columns.
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
        .filter(column -> V2_FINAL_TABLE_METADATA_COLUMNS.stream()
            .noneMatch(airbyteColumnName -> airbyteColumnName.equals(column.getKey())))
        .collect(LinkedHashMap::new,
            (map, column) -> map.put(column.getKey(), column.getValue().type()),
            LinkedHashMap::putAll);

    return actualColumns.equals(intendedColumns);
  }

  @Override
  public void commitDestinationStates(final Map<StreamId, DestinationState> destinationStates) throws Exception {
    if (destinationStates.isEmpty()) {
      return;
    }

    // Delete all state records where the stream name+namespace match one of our states
    String deleteStates = getDslContext().deleteFrom(table(quotedName(rawTableSchemaName, DESTINATION_STATE_TABLE_NAME)))
        .where(destinationStates.keySet().stream()
            .map(streamId -> field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME)).eq(streamId.originalName())
                .and(field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE)).eq(streamId.originalNamespace())))
            .reduce(
                DSL.falseCondition(),
                Condition::or))
        .getSQL(ParamType.INLINED);

    // Reinsert all of our states
    @NotNull
    InsertValuesStep4<Record, String, String, String, String> insertStatesStep =
        getDslContext().insertInto(table(quotedName(rawTableSchemaName, DESTINATION_STATE_TABLE_NAME)))
            .columns(
                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAME), String.class),
                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_NAMESPACE), String.class),
                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_STATE), String.class),
                // This field is a timestamptz, but it's easier to just insert a string
                // and assume the destination can cast it appropriately.
                // Destination-specific timestamp syntax is weird and annoying.
                field(quotedName(DESTINATION_STATE_TABLE_COLUMN_UPDATED_AT), String.class));
    for (Map.Entry<StreamId, DestinationState> destinationState : destinationStates.entrySet()) {
      final StreamId streamId = destinationState.getKey();
      final String stateJson = Jsons.serialize(destinationState.getValue());
      insertStatesStep = insertStatesStep.values(streamId.originalName(), streamId.originalNamespace(), stateJson, OffsetDateTime.now().toString());
    }
    String insertStates = insertStatesStep.getSQL(ParamType.INLINED);

    jdbcDatabase.executeWithinTransaction(List.of(deleteStates, insertStates));
  }

  /**
   * Convert to the TYPE_NAME retrieved from {@link java.sql.DatabaseMetaData#getColumns}
   *
   * @param airbyteType
   * @return
   */
  protected abstract String toJdbcTypeName(final AirbyteType airbyteType);

  protected abstract DestinationState toDestinationState(final JsonNode json);

}
