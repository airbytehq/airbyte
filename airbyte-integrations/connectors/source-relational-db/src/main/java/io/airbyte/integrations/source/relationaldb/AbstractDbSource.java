/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import static io.airbyte.integrations.base.errors.messages.ErrorMessage.getErrorMessage;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.db.AbstractDatabase;
import io.airbyte.db.IncrementalUtils;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.InvalidCursorInfoUtil.InvalidCursorInfo;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.source.relationaldb.state.StateManagerFactory;
import io.airbyte.integrations.util.ConnectorExceptionUtil;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaPrimitiveUtil.JsonSchemaPrimitive;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class contains helper functions and boilerplate for implementing a source connector for a DB
 * source of both non-relational and relational type
 */
public abstract class AbstractDbSource<DataType, Database extends AbstractDatabase> extends
    BaseConnector implements Source, AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractDbSource.class);
  // TODO: Remove when the flag is not use anymore
  private final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    try {
      final Database database = createDatabase(config);
      for (final CheckedConsumer<Database, Exception> checkOperation : getCheckOperations(config)) {
        checkOperation.accept(database);
      }

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final ConnectionErrorException ex) {
      final String message = getErrorMessage(ex.getStateCode(), ex.getErrorCode(),
          ex.getExceptionMessage(), ex);
      AirbyteTraceMessageUtility.emitConfigErrorTrace(ex, message);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(message);
    } catch (final Exception e) {
      LOGGER.info("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage(String.format(ConnectorExceptionUtil.COMMON_EXCEPTION_MESSAGE_TEMPLATE, e.getMessage()));
    } finally {
      close();
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    try {
      final Database database = createDatabase(config);
      final List<TableInfo<CommonField<DataType>>> tableInfos = discoverInternal(database);
      final Map<String, List<String>> fullyQualifiedTableNameToPrimaryKeys = discoverPrimaryKeys(
          database, tableInfos);
      return DbSourceDiscoverUtil.convertTableInfosToAirbyteCatalog(tableInfos, fullyQualifiedTableNameToPrimaryKeys, this::getAirbyteType);
    } finally {
      close();
    }
  }

  /**
   * Creates a list of AirbyteMessageIterators with all the streams selected in a configured catalog
   *
   * @param config - integration-specific configuration object as json. e.g. { "username": "airbyte",
   *        "password": "super secure" }
   * @param catalog - schema of the incoming messages.
   * @param state - state of the incoming messages.
   * @return AirbyteMessageIterator with all the streams that are to be synced
   * @throws Exception
   */
  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state)
      throws Exception {
    final StateManager stateManager =
        StateManagerFactory.createStateManager(AirbyteStateType.LEGACY,
            deserializeInitialState(state, config, featureFlags.useStreamCapableState()), catalog);
    final Instant emittedAt = Instant.now();

    final Database database = createDatabase(config);

    final Map<String, TableInfo<CommonField<DataType>>> fullyQualifiedTableNameToInfo =
        discoverInternal(database)
            .stream()
            .collect(Collectors.toMap(t -> String.format("%s.%s", t.getNameSpace(), t.getName()),
                Function
                    .identity()));

    validateCursorFieldForIncrementalTables(fullyQualifiedTableNameToInfo, catalog, database);

    DbSourceDiscoverUtil.logSourceSchemaChange(fullyQualifiedTableNameToInfo, catalog, this::getAirbyteType);

    final List<AutoCloseableIterator<AirbyteMessage>> incrementalIterators =
        getSelectedIterators(
          database,
          catalog,
          fullyQualifiedTableNameToInfo,
          stateManager,
          emittedAt,
          SyncMode.FULL_REFRESH);
    final List<AutoCloseableIterator<AirbyteMessage>> fullRefreshIterators =
        getSelectedIterators(
            database,
            catalog,
            fullyQualifiedTableNameToInfo,
            stateManager,
            emittedAt,
            SyncMode.INCREMENTAL);

    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = Stream
        .of(incrementalIterators, fullRefreshIterators)
        .flatMap(Collection::stream)
        .collect(Collectors.toList());

    return AutoCloseableIterators
        .appendOnClose(AutoCloseableIterators.concatWithEagerClose(iteratorList), () -> {
          LOGGER.info("Closing database connection pool.");
          Exceptions.toRuntime(this::close);
          LOGGER.info("Closed database connection pool.");
        });
  }

  private void validateCursorFieldForIncrementalTables(
                                                       final Map<String, TableInfo<CommonField<DataType>>> tableNameToTable,
                                                       final ConfiguredAirbyteCatalog catalog,
                                                       final Database database)
      throws SQLException {
    final List<InvalidCursorInfo> tablesWithInvalidCursor = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      final AirbyteStream stream = airbyteStream.getStream();
      final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getNamespace(),
          stream.getName());
      final boolean hasSourceDefinedCursor =
          !Objects.isNull(airbyteStream.getStream().getSourceDefinedCursor())
              && airbyteStream.getStream().getSourceDefinedCursor();
      if (!tableNameToTable.containsKey(fullyQualifiedTableName)
          || airbyteStream.getSyncMode() != SyncMode.INCREMENTAL || hasSourceDefinedCursor) {
        continue;
      }

      final TableInfo<CommonField<DataType>> table = tableNameToTable
          .get(fullyQualifiedTableName);
      final Optional<String> cursorField = IncrementalUtils.getCursorFieldOptional(airbyteStream);
      if (cursorField.isEmpty()) {
        continue;
      }
      final DataType cursorType = table.getFields().stream()
          .filter(info -> info.getName().equals(cursorField.get()))
          .map(CommonField::getType)
          .findFirst()
          .orElseThrow();

      if (!isCursorType(cursorType)) {
        tablesWithInvalidCursor.add(
            new InvalidCursorInfo(fullyQualifiedTableName, cursorField.get(),
                cursorType.toString(), "Unsupported cursor type"));
        continue;
      }

      if (!verifyCursorColumnValues(database, stream.getNamespace(), stream.getName(), cursorField.get())) {
        tablesWithInvalidCursor.add(
            new InvalidCursorInfo(fullyQualifiedTableName, cursorField.get(),
                cursorType.toString(), "Cursor column contains NULL value"));
      }
    }

    if (!tablesWithInvalidCursor.isEmpty()) {
      throw new ConfigErrorException(
          InvalidCursorInfoUtil.getInvalidCursorConfigMessage(tablesWithInvalidCursor));
    }
  }

  /**
   * Verify that cursor column allows syncing to go through.
   *
   * @param database database
   * @return true if syncing can go through. false otherwise
   * @throws SQLException exception
   */
  protected boolean verifyCursorColumnValues(final Database database, final String schema, final String tableName, final String columnName)
      throws SQLException {
    /* no-op */
    return true;
  }

  /**
   * Creates a list of read iterators for each stream within an ConfiguredAirbyteCatalog
   *
   * @param database Source Database
   * @param catalog List of streams (e.g. database tables or API endpoints) with settings on sync mode
   * @param tableNameToTable Mapping of table name to table
   * @param stateManager Manager used to track the state of data synced by the connector
   * @param emittedAt Time when data was emitted from the Source database
   * @param syncMode the sync mode for which we want to grab the required iterators
   * @return List of AirbyteMessageIterators containing all iterators for a catalog
   */
  private List<AutoCloseableIterator<AirbyteMessage>> getSelectedIterators(
                                                                           final Database database,
                                                                           final ConfiguredAirbyteCatalog catalog,
                                                                           final Map<String, TableInfo<CommonField<DataType>>> tableNameToTable,
                                                                           final StateManager stateManager,
                                                                           final Instant emittedAt,
                                                                           final SyncMode syncMode) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      if (airbyteStream.getSyncMode().equals(syncMode)) {
        final AirbyteStream stream = airbyteStream.getStream();
        final String fullyQualifiedTableName = DbSourceDiscoverUtil.getFullyQualifiedTableName(stream.getNamespace(),
            stream.getName());
        if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
          LOGGER
              .info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
          continue;
        }

        final TableInfo<CommonField<DataType>> table = tableNameToTable
            .get(fullyQualifiedTableName);
        final AutoCloseableIterator<AirbyteMessage> tableReadIterator = createReadIterator(
            database,
            airbyteStream,
            table,
            stateManager,
            emittedAt);
        iteratorList.add(tableReadIterator);
      }
    }

    return iteratorList;
  }

  /**
   * ReadIterator is used to retrieve records from a source connector
   *
   * @param database Source Database
   * @param airbyteStream represents an ingestion source (e.g. API endpoint or database table)
   * @param table information in tabular format
   * @param stateManager Manager used to track the state of data synced by the connector
   * @param emittedAt Time when data was emitted from the Source database
   * @return
   */
  private AutoCloseableIterator<AirbyteMessage> createReadIterator(final Database database,
                                                                   final ConfiguredAirbyteStream airbyteStream,
                                                                   final TableInfo<CommonField<DataType>> table,
                                                                   final StateManager stateManager,
                                                                   final Instant emittedAt) {
    final String streamName = airbyteStream.getStream().getName();
    final String namespace = airbyteStream.getStream().getNamespace();
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName,
        namespace);
    final Set<String> selectedFieldsInCatalog = CatalogHelpers.getTopLevelFieldNames(airbyteStream);
    final List<String> selectedDatabaseFields = table.getFields()
        .stream()
        .map(CommonField::getName)
        .filter(selectedFieldsInCatalog::contains)
        .collect(Collectors.toList());

    final AutoCloseableIterator<AirbyteMessage> iterator;
    // checks for which sync mode we're using based on the configured airbytestream
    // this is where the bifurcation between full refresh and incremental
    if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
      final String cursorField = IncrementalUtils.getCursorField(airbyteStream);
      final Optional<CursorInfo> cursorInfo = stateManager.getCursorInfo(pair);

      final AutoCloseableIterator<AirbyteMessage> airbyteMessageIterator;
      if (cursorInfo.map(CursorInfo::getCursor).isPresent()) {
        airbyteMessageIterator = getIncrementalStream(
            database,
            airbyteStream,
            selectedDatabaseFields,
            table,
            cursorInfo.get(),
            emittedAt);
      } else {
        airbyteMessageIterator = getFullRefreshStream(database, streamName, namespace,
            selectedDatabaseFields, table, emittedAt);
      }

      final JsonSchemaPrimitive cursorType = IncrementalUtils.getCursorType(airbyteStream,
          cursorField);

      iterator = AutoCloseableIterators.transform(
          autoCloseableIterator -> new StateDecoratingIterator(
              autoCloseableIterator,
              stateManager,
              pair,
              cursorField,
              cursorInfo.map(CursorInfo::getCursor).orElse(null),
              cursorType,
              getStateEmissionFrequency()),
          airbyteMessageIterator);
    } else if (airbyteStream.getSyncMode() == SyncMode.FULL_REFRESH) {
      iterator = getFullRefreshStream(database, streamName, namespace, selectedDatabaseFields,
          table, emittedAt);
    } else if (airbyteStream.getSyncMode() == null) {
      throw new IllegalArgumentException(
          String.format("%s requires a source sync mode", this.getClass()));
    } else {
      throw new IllegalArgumentException(
          String.format("%s does not support sync mode: %s.", this.getClass(),
              airbyteStream.getSyncMode()));
    }

    final AtomicLong recordCount = new AtomicLong();
    return AutoCloseableIterators.transform(iterator, r -> {
      final long count = recordCount.incrementAndGet();
      if (count % 10000 == 0) {
        LOGGER.info("Reading stream {}. Records read: {}", streamName, count);
      }
      return r;
    });
  }

  /**
   * @param database Source Database
   * @param airbyteStream represents an ingestion source (e.g. API endpoint or database table)
   * @param selectedDatabaseFields subset of database fields selected for replication
   * @param table information in tabular format
   * @param cursorInfo state of where to start the sync from
   * @param emittedAt Time when data was emitted from the Source database
   * @return AirbyteMessage Iterator that
   */
  private AutoCloseableIterator<AirbyteMessage> getIncrementalStream(final Database database,
                                                                     final ConfiguredAirbyteStream airbyteStream,
                                                                     final List<String> selectedDatabaseFields,
                                                                     final TableInfo<CommonField<DataType>> table,
                                                                     final CursorInfo cursorInfo,
                                                                     final Instant emittedAt) {
    final String streamName = airbyteStream.getStream().getName();
    final String namespace = airbyteStream.getStream().getNamespace();
    final String cursorField = IncrementalUtils.getCursorField(airbyteStream);
    final DataType cursorType = table.getFields().stream()
        .filter(info -> info.getName().equals(cursorField))
        .map(CommonField::getType)
        .findFirst()
        .orElseThrow();

    Preconditions.checkState(
        table.getFields().stream().anyMatch(f -> f.getName().equals(cursorField)),
        String.format("Could not find cursor field %s in table %s", cursorField, table.getName()));

    final AutoCloseableIterator<JsonNode> queryIterator = queryTableIncremental(
        database,
        selectedDatabaseFields,
        table.getNameSpace(),
        table.getName(),
        cursorInfo,
        cursorType);

    return getMessageIterator(queryIterator, streamName, namespace, emittedAt.toEpochMilli());
  }

  /**
   * Creates a AirbyteMessageIterator that contains all records for a database source connection
   *
   * @param database Source Database
   * @param streamName name of an individual stream in which a stream represents a source (e.g. API
   *        endpoint or database table)
   * @param namespace Namespace of the database (e.g. public)
   * @param selectedDatabaseFields List of all interested database column names
   * @param table information in tabular format
   * @param emittedAt Time when data was emitted from the Source database
   * @return AirbyteMessageIterator with all records for a database source
   */
  private AutoCloseableIterator<AirbyteMessage> getFullRefreshStream(final Database database,
                                                                     final String streamName,
                                                                     final String namespace,
                                                                     final List<String> selectedDatabaseFields,
                                                                     final TableInfo<CommonField<DataType>> table,
                                                                     final Instant emittedAt) {
    final AutoCloseableIterator<JsonNode> queryStream =
        queryTableFullRefresh(database, selectedDatabaseFields, table.getNameSpace(),
            table.getName());
    return getMessageIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
  }

  private static AutoCloseableIterator<AirbyteMessage> getMessageIterator(
                                                                          final AutoCloseableIterator<JsonNode> recordIterator,
                                                                          final String streamName,
                                                                          final String namespace,
                                                                          final long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withNamespace(namespace)
            .withEmittedAt(emittedAt)
            .withData(r)));
  }

  /**
   * Creates a database instance using the database spec config.
   *
   * @param config database spec config
   * @return database instance
   * @throws Exception might throw an error during connection to database
   */
  protected abstract Database createDatabase(JsonNode config) throws Exception;

  /**
   * Configures a list of operations that can be used to check the connection to the source.
   *
   * @return list of consumers that run queries for the check command.
   */
  protected abstract List<CheckedConsumer<Database, Exception>> getCheckOperations(JsonNode config)
      throws Exception;

  /**
   * Map source types to Airbyte types
   *
   * @param columnType source data type
   * @return airbyte data type
   */
  protected abstract JsonSchemaType getAirbyteType(DataType columnType);

  /**
   * Discover all available tables in the source database.
   *
   * @param database source database
   * @return list of the source tables
   * @throws Exception access to the database might lead to an exceptions.
   */
  protected abstract List<TableInfo<CommonField<DataType>>> discoverInternal(
                                                                             final Database database)
      throws Exception;

  /**
   * Discover Primary keys for each table and @return a map of namespace.table name to their
   * associated list of primary key fields.
   *
   * @param database source database
   * @param tableInfos list of tables
   * @return map of namespace.table and primary key fields.
   */
  protected abstract Map<String, List<String>> discoverPrimaryKeys(Database database,
                                                                   List<TableInfo<CommonField<DataType>>> tableInfos);

  /**
   * Read all data from a table.
   *
   * @param database source database
   * @param columnNames interested column names
   * @param schemaName table namespace
   * @param tableName target table
   * @return iterator with read data
   */
  protected abstract AutoCloseableIterator<JsonNode> queryTableFullRefresh(final Database database,
                                                                           final List<String> columnNames,
                                                                           final String schemaName,
                                                                           final String tableName);

  /**
   * Read incremental data from a table. Incremental read should return only records where cursor
   * column value is bigger than cursor. Note that if the connector needs to emit intermediate state
   * (i.e. {@link AbstractDbSource#getStateEmissionFrequency} > 0), the incremental query must be
   * sorted by the cursor field.
   *
   * @return iterator with read data
   */
  protected abstract AutoCloseableIterator<JsonNode> queryTableIncremental(Database database,
                                                                           List<String> columnNames,
                                                                           String schemaName,
                                                                           String tableName,
                                                                           CursorInfo cursorInfo,
                                                                           DataType cursorFieldType);

  /**
   * When larger than 0, the incremental iterator will emit intermediate state for every N records.
   * Please note that if intermediate state emission is enabled, the incremental query must be ordered
   * by the cursor field.
   */
  protected int getStateEmissionFrequency() {
    return 0;
  }

  /**
   * @return list of fields that could be used as cursors
   */
  protected abstract boolean isCursorType(DataType type);

  /**
   * Deserializes the state represented as JSON into an object representation.
   *
   * @param initialStateJson The state as JSON.
   * @param config The connector configuration.
   * @return The deserialized object representation of the state.
   */
  protected List<AirbyteStateMessage> deserializeInitialState(final JsonNode initialStateJson,
                                                              final JsonNode config,
                                                              final boolean useStreamCapableState) {
    final Optional<StateWrapper> typedState = StateMessageHelper.getTypedState(initialStateJson,
        useStreamCapableState);
    if (typedState.isPresent()) {
      return List.of(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY)
          .withData(typedState.get().getLegacyState()));
    } else {
      // For backwards compatibility with existing connectors
      return List.of(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY)
          .withData(Jsons.jsonNode(new DbState())));
    }
  }
}
