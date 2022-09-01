/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.type.Types;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.db.AbstractDatabase;
import io.airbyte.db.IncrementalUtils;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.source.relationaldb.state.StateManagerFactory;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class contains helper functions and boilerplate for implementing a source connector for a
 * DB source of both non-relational and relational type
 */
public abstract class AbstractDbSource<DataType, Database extends AbstractDatabase> extends
    BaseConnector implements Source, AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractDbSource.class);
  // TODO: Remove when the flag is not use anymore
  private final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

  @Override
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    try {
      final Database database = createDatabaseInternal(config);
      for (final CheckedConsumer<Database, Exception> checkOperation : getCheckOperations(config)) {
        checkOperation.accept(database);
      }

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (final Exception e) {
      LOGGER.info("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. Error: " + e.getMessage());
    } finally {
      close();
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    try {
      final Database database = createDatabaseInternal(config);
      final List<AirbyteStream> streams = getTables(database).stream()
          .map(tableInfo -> CatalogHelpers
              .createAirbyteStream(tableInfo.getName(), tableInfo.getNameSpace(),
                  tableInfo.getFields())
              .withSupportedSyncModes(
                  tableInfo.getCursorFields() != null && tableInfo.getCursorFields().isEmpty() ? Lists.newArrayList(SyncMode.FULL_REFRESH)
                      : Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
              .withSourceDefinedPrimaryKey(Types.boxToListofList(tableInfo.getPrimaryKeys())))
          .collect(Collectors.toList());
      return new AirbyteCatalog().withStreams(streams);
    } finally {
      close();
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state)
      throws Exception {
    final StateManager stateManager =
        StateManagerFactory.createStateManager(getSupportedStateType(config), deserializeInitialState(state, config), catalog);
    final Instant emittedAt = Instant.now();

    final Database database = createDatabaseInternal(config);

    final Map<String, TableInfo<CommonField<DataType>>> fullyQualifiedTableNameToInfo =
        discoverWithoutSystemTables(database)
            .stream()
            .collect(Collectors.toMap(t -> String.format("%s.%s", t.getNameSpace(), t.getName()), Function
                .identity()));

    final List<AutoCloseableIterator<AirbyteMessage>> incrementalIterators =
        getIncrementalIterators(database, catalog, fullyQualifiedTableNameToInfo, stateManager, emittedAt);
    final List<AutoCloseableIterator<AirbyteMessage>> fullRefreshIterators =
        getFullRefreshIterators(database, catalog, fullyQualifiedTableNameToInfo, stateManager, emittedAt);
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

  protected List<TableInfo<CommonField<DataType>>> discoverWithoutSystemTables(final Database database) throws Exception {
    final Set<String> systemNameSpaces = getExcludedInternalNameSpaces();
    final List<TableInfo<CommonField<DataType>>> discoveredTables = discoverInternal(database);
    return (systemNameSpaces == null || systemNameSpaces.isEmpty() ? discoveredTables
        : discoveredTables.stream().filter(table -> !systemNameSpaces.contains(table.getNameSpace())).collect(
            Collectors.toList()));
  }

  protected List<AutoCloseableIterator<AirbyteMessage>> getFullRefreshIterators(final Database database,
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final Map<String, TableInfo<CommonField<DataType>>> tableNameToTable,
                                                                                final StateManager stateManager,
                                                                                final Instant emittedAt) {
    return getSelectedIterators(
        database,
        catalog,
        tableNameToTable,
        stateManager,
        emittedAt,
        configuredStream -> configuredStream.getSyncMode().equals(SyncMode.FULL_REFRESH));
  }

  protected List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final Database database,
                                                                                final ConfiguredAirbyteCatalog catalog,
                                                                                final Map<String, TableInfo<CommonField<DataType>>> tableNameToTable,
                                                                                final StateManager stateManager,
                                                                                final Instant emittedAt) {
    return getSelectedIterators(
        database,
        catalog,
        tableNameToTable,
        stateManager,
        emittedAt,
        configuredStream -> configuredStream.getSyncMode().equals(SyncMode.INCREMENTAL));
  }

  protected List<AutoCloseableIterator<AirbyteMessage>> getSelectedIterators(final Database database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<DataType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt,
                                                                             final Predicate<ConfiguredAirbyteStream> selector) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      if (selector.test(airbyteStream)) {
        final AirbyteStream stream = airbyteStream.getStream();
        final String fullyQualifiedTableName = getFullyQualifiedTableName(stream.getNamespace(),
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

  protected AutoCloseableIterator<AirbyteMessage> createReadIterator(final Database database,
                                                                     final ConfiguredAirbyteStream airbyteStream,
                                                                     final TableInfo<CommonField<DataType>> table,
                                                                     final StateManager stateManager,
                                                                     final Instant emittedAt) {
    final String streamName = airbyteStream.getStream().getName();
    final String namespace = airbyteStream.getStream().getNamespace();
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);
    final Set<String> selectedFieldsInCatalog = CatalogHelpers.getTopLevelFieldNames(airbyteStream);
    final List<String> selectedDatabaseFields = table.getFields()
        .stream()
        .map(CommonField::getName)
        .filter(selectedFieldsInCatalog::contains)
        .collect(Collectors.toList());

    final AutoCloseableIterator<AirbyteMessage> iterator;
    if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
      final String cursorField = IncrementalUtils.getCursorField(airbyteStream);
      final Optional<String> cursorOptional = stateManager.getCursor(pair);

      final AutoCloseableIterator<AirbyteMessage> airbyteMessageIterator;
      if (cursorOptional.isPresent()) {
        airbyteMessageIterator = getIncrementalStream(database, airbyteStream, selectedDatabaseFields, table, cursorOptional.get(), emittedAt);
      } else {
        // if no cursor is present then this is the first read for is the same as doing a full refresh read.
        airbyteMessageIterator = getFullRefreshStream(database, streamName, namespace, selectedDatabaseFields, table, emittedAt);
      }

      final JsonSchemaPrimitive cursorType = IncrementalUtils.getCursorType(airbyteStream, cursorField);

      iterator = AutoCloseableIterators.transform(autoCloseableIterator -> new StateDecoratingIterator(
          autoCloseableIterator,
          stateManager,
          pair,
          cursorField,
          cursorOptional.orElse(null),
          cursorType,
          getStateEmissionFrequency()),
          airbyteMessageIterator);
    } else if (airbyteStream.getSyncMode() == SyncMode.FULL_REFRESH) {
      iterator = getFullRefreshStream(database, streamName, namespace, selectedDatabaseFields, table, emittedAt);
    } else if (airbyteStream.getSyncMode() == null) {
      throw new IllegalArgumentException(String.format("%s requires a source sync mode", this.getClass()));
    } else {
      throw new IllegalArgumentException(String.format("%s does not support sync mode: %s.", this.getClass(), airbyteStream.getSyncMode()));
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

  protected AutoCloseableIterator<AirbyteMessage> getIncrementalStream(final Database database,
                                                                       final ConfiguredAirbyteStream airbyteStream,
                                                                       final List<String> selectedDatabaseFields,
                                                                       final TableInfo<CommonField<DataType>> table,
                                                                       final String cursor,
                                                                       final Instant emittedAt) {
    final String streamName = airbyteStream.getStream().getName();
    final String namespace = airbyteStream.getStream().getNamespace();
    final String cursorField = IncrementalUtils.getCursorField(airbyteStream);
    final DataType cursorType = table.getFields().stream()
        .filter(info -> info.getName().equals(cursorField))
        .map(CommonField::getType)
        .findFirst()
        .orElseThrow();

    Preconditions.checkState(table.getFields().stream().anyMatch(f -> f.getName().equals(cursorField)),
        String.format("Could not find cursor field %s in table %s", cursorField, table.getName()));

    final AutoCloseableIterator<JsonNode> queryIterator = queryTableIncremental(
        database,
        selectedDatabaseFields,
        table.getNameSpace(),
        table.getName(),
        cursorField,
        cursorType,
        cursor);

    return getMessageIterator(queryIterator, streamName, namespace, emittedAt.toEpochMilli());
  }

  protected AutoCloseableIterator<AirbyteMessage> getFullRefreshStream(final Database database,
                                                                       final String streamName,
                                                                       final String namespace,
                                                                       final List<String> selectedDatabaseFields,
                                                                       final TableInfo<CommonField<DataType>> table,
                                                                       final Instant emittedAt) {
    final AutoCloseableIterator<JsonNode> queryStream =
        queryTableFullRefresh(database, selectedDatabaseFields, table.getNameSpace(), table.getName());
    return getMessageIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
  }

  protected String getFullyQualifiedTableName(final String nameSpace, final String tableName) {
    return nameSpace != null ? nameSpace + "." + tableName : tableName;
  }

  public AutoCloseableIterator<AirbyteMessage> getMessageIterator(final AutoCloseableIterator<JsonNode> recordIterator,
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
   * Get list of source tables/data structures for schema discovery.
   *
   * @param database instance
   * @return list of table/data structure info
   * @throws Exception might throw an error during connection to database
   */
  protected List<TableInfo<Field>> getTables(final Database database) throws Exception {
    final List<TableInfo<CommonField<DataType>>> tableInfos = discoverWithoutSystemTables(database);
    final Map<String, List<String>> fullyQualifiedTableNameToPrimaryKeys = discoverPrimaryKeys(database, tableInfos);

    return tableInfos.stream()
        .map(t -> {
          // some databases return multiple copies of the same record for a column (e.g. redshift) because
          // they have at least once delivery guarantees. we want to dedupe these, but first we check that the
          // records are actually the same and provide a good error message if they are not.
          assertColumnsWithSameNameAreSame(t.getNameSpace(), t.getName(), t.getFields());
          final List<Field> fields = t.getFields()
              .stream()
              .map(this::toField)
              .distinct()
              .collect(Collectors.toList());
          final String fullyQualifiedTableName = getFullyQualifiedTableName(t.getNameSpace(), t.getName());
          final List<String> primaryKeys = fullyQualifiedTableNameToPrimaryKeys.getOrDefault(fullyQualifiedTableName, Collections
              .emptyList());
          return TableInfo.<Field>builder().nameSpace(t.getNameSpace()).name(t.getName()).fields(fields).primaryKeys(primaryKeys)
              .cursorFields(t.getCursorFields())
              .build();
        })
        .collect(Collectors.toList());
  }

  protected Field toField(final CommonField<DataType> field) {
    if (getType(field.getType()) == JsonSchemaType.OBJECT && field.getProperties() != null && !field.getProperties().isEmpty()) {
      final var properties = field.getProperties().stream().map(this::toField).toList();
      return Field.of(field.getName(), getType(field.getType()), properties);
    } else {
      return Field.of(field.getName(), getType(field.getType()));
    }
  }

  protected void assertColumnsWithSameNameAreSame(final String nameSpace, final String tableName, final List<CommonField<DataType>> columns) {
    columns.stream()
        .collect(Collectors.groupingBy(CommonField<DataType>::getName))
        .values()
        .forEach(columnsWithSameName -> {
          final CommonField<DataType> comparisonColumn = columnsWithSameName.get(0);
          columnsWithSameName.forEach(column -> {
            if (!column.equals(comparisonColumn)) {
              throw new RuntimeException(
                  String.format("Found multiple columns with same name: %s in table: %s.%s but the columns are not the same. columns: %s",
                      comparisonColumn.getName(), nameSpace, tableName, columns));
            }
          });
        });
  }

  /**
   * @param database - The database where from privileges for tables will be consumed
   * @param schema - The schema where from privileges for tables will be consumed
   * @return Set with privileges for tables for current DB-session user The method is responsible for
   *         SELECT-ing the table with privileges. In some cases such SELECT doesn't require (e.g. in
   *         Oracle DB - the schema is the user, you cannot REVOKE a privilege on a table from its
   *         owner).
   */
  public <T> Set<T> getPrivilegesTableForCurrentUser(final JdbcDatabase database, final String schema) throws SQLException {
    return Collections.emptySet();
  }

  /**
   * Map a database implementation-specific configuration to json object that adheres to the database
   * config spec. See resources/spec.json.
   *
   * @param config database implementation-specific configuration.
   * @return database spec config
   */
  public abstract JsonNode toDatabaseConfig(JsonNode config);

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
  public abstract List<CheckedConsumer<Database, Exception>> getCheckOperations(JsonNode config)
      throws Exception;

  /**
   * Map source types and Airbyte types
   *
   * @param columnType source data type
   * @return airbyte data type
   */
  protected abstract JsonSchemaType getType(DataType columnType);

  /**
   * Get list of system namespaces(schemas) in order to exclude them from the discover result list.
   *
   * @return set of system namespaces(schemas) to be excluded
   */
  public abstract Set<String> getExcludedInternalNameSpaces();

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
   * Discovers all available tables within a schema in the source database.
   *
   * @param database - source database
   * @param schema - source schema
   * @return list of source tables
   * @throws Exception - access to the database might lead to exceptions.
   */
  protected abstract List<TableInfo<CommonField<DataType>>> discoverInternal(final Database database, String schema)
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
   * Returns quote symbol of the database
   *
   * @return quote symbol
   */
  protected abstract String getQuoteString();

  /**
   * Read all data from a table.
   *
   * @param database source database
   * @param columnNames interested column names
   * @param schemaName table namespace
   * @param tableName target table
   * @return iterator with read data
   */
  public abstract AutoCloseableIterator<JsonNode> queryTableFullRefresh(final Database database,
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
  public abstract AutoCloseableIterator<JsonNode> queryTableIncremental(Database database,
                                                                        List<String> columnNames,
                                                                        String schemaName,
                                                                        String tableName,
                                                                        String cursorField,
                                                                        DataType cursorFieldType,
                                                                        String cursorValue);

  /**
   * When larger than 0, the incremental iterator will emit intermediate state for every N records.
   * Please note that if intermediate state emission is enabled, the incremental query must be ordered
   * by the cursor field.
   */
  protected int getStateEmissionFrequency() {
    return 0;
  }

  /**
   *
   * @return list of fields that could be used as cursors
   */
  public abstract boolean isCursorType(DataType type);

  private Database createDatabaseInternal(final JsonNode sourceConfig) throws Exception {
    final Database database = createDatabase(sourceConfig);
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(toDatabaseConfig(sourceConfig));
    return database;
  }

  /**
   * Deserializes the state represented as JSON into an object representation.
   *
   * @param initialStateJson The state as JSON.
   * @param config The connector configuration.
   * @return The deserialized object representation of the state.
   */
  protected List<AirbyteStateMessage> deserializeInitialState(final JsonNode initialStateJson, final JsonNode config) {
    final Optional<StateWrapper> typedState = StateMessageHelper.getTypedState(initialStateJson, featureFlags.useStreamCapableState());
    return typedState.map((state) -> {
      switch (state.getStateType()) {
        case GLOBAL:
          return List.of(state.getGlobal());
        case STREAM:
          return state.getStateMessages();
        case LEGACY:
        default:
          return List.of(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY).withData(state.getLegacyState()));
      }
    }).orElse(generateEmptyInitialState(config));
  }

  /**
   * Generates an empty, initial state for use by the connector.
   *
   * @param config The connector configuration.
   * @return The empty, initial state.
   */
  protected List<AirbyteStateMessage> generateEmptyInitialState(final JsonNode config) {
    // For backwards compatibility with existing connectors
    return List.of(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY).withData(Jsons.jsonNode(new DbState())));
  }

  /**
   * Returns the {@link AirbyteStateType} supported by this connector.
   *
   * @param config The connector configuration.
   * @return A {@link AirbyteStateType} representing the state supported by this connector.
   */
  protected AirbyteStateType getSupportedStateType(final JsonNode config) {
    return AirbyteStateType.LEGACY;
  }

}
