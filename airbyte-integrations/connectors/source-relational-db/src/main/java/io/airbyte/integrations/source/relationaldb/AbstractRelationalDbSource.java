/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.relationaldb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.Lists;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.type.Types;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.IncrementalUtils;
import io.airbyte.db.jdbc.SqlDatabase;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.models.JdbcState;
import io.airbyte.protocol.models.AbstractField;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.sql.SQLException;
import java.sql.SQLType;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.StringJoiner;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractRelationalDbSource<T extends SQLType, K extends SqlDatabase> extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractRelationalDbSource.class);

  public abstract Set<String> getExcludedInternalNameSpaces();

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (final K database = createDatabaseInternal(config)) {
      for (CheckedConsumer<K, Exception> checkOperation : getCheckOperations(config)) {
        checkOperation.accept(database);
      }

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.info("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration. Error: " + e.getMessage());
    }
  }

  /**
   * Map a database implementation-specific configuration to json object that adheres to the
   * AbstractJdbcSource config spec. See resources/spec.json.
   *
   * @param config database implementation-specific configuration.
   * @return jdbc spec.
   */
  public abstract JsonNode toDatabaseConfig(JsonNode config);

  /**
   * Configures a list of operations that can be used to check the connection to the source.
   *
   * @return list of consumers that run queries for the check command.
   */
  public abstract List<CheckedConsumer<K, Exception>> getCheckOperations(JsonNode config) throws Exception;

  @Override
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    try (final K database = createDatabaseInternal(config)) {
      List<AirbyteStream> streams = getTables(database).stream()
          .map(tableInfo -> CatalogHelpers
              .createAirbyteStream(tableInfo.getName(), tableInfo.getNameSpace(), tableInfo.getFields())
              .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
              .withSourceDefinedPrimaryKey(Types.boxToListofList(tableInfo.getPrimaryKeys())))
          .collect(Collectors.toList());
      return new AirbyteCatalog().withStreams(streams);
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
    final StateManager stateManager = new StateManager(
        state == null ? StateManager.emptyState() : Jsons.object(state, JdbcState.class),
        catalog);
    final Instant emittedAt = Instant.now();

    final K database = createDatabaseInternal(config);

    final Map<String, TableInfo<AbstractField<T>>> fullyQualifiedTableNameToInfo =
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
          Exceptions.toRuntime(database::close);
          LOGGER.info("Closed database connection pool.");
        });
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(K database,
                                                                             ConfiguredAirbyteCatalog catalog,
                                                                             Map<String, TableInfo<AbstractField<T>>> tableNameToTable,
                                                                             StateManager stateManager,
                                                                             Instant emittedAt) {
    return getSelectedIterators(
        database,
        catalog,
        tableNameToTable,
        stateManager,
        emittedAt,
        configuredStream -> configuredStream.getSyncMode().equals(SyncMode.INCREMENTAL));
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getFullRefreshIterators(K database,
                                                                             ConfiguredAirbyteCatalog catalog,
                                                                             Map<String, TableInfo<AbstractField<T>>> tableNameToTable,
                                                                             StateManager stateManager,
                                                                             Instant emittedAt) {
    return getSelectedIterators(
        database,
        catalog,
        tableNameToTable,
        stateManager,
        emittedAt,
        configuredStream -> configuredStream.getSyncMode().equals(SyncMode.FULL_REFRESH));
  }

  private List<AutoCloseableIterator<AirbyteMessage>> getSelectedIterators(K database,
                                                                           ConfiguredAirbyteCatalog catalog,
                                                                           Map<String, TableInfo<AbstractField<T>>> tableNameToTable,
                                                                           StateManager stateManager,
                                                                           Instant emittedAt,
                                                                           Predicate<ConfiguredAirbyteStream> selector) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();
    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      if (selector.test(airbyteStream)) {
        final AirbyteStream stream = airbyteStream.getStream();
        final String fullyQualifiedTableName = getFullyQualifiedTableName(stream.getNamespace(), stream.getName());
        if (!tableNameToTable.containsKey(fullyQualifiedTableName)) {
          LOGGER.info("Skipping stream {} because it is not in the source", fullyQualifiedTableName);
          continue;
        }

        final TableInfo<AbstractField<T>> table = tableNameToTable.get(fullyQualifiedTableName);
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

  private AutoCloseableIterator<AirbyteMessage> createReadIterator(K database,
                                                                   ConfiguredAirbyteStream airbyteStream,
                                                                   TableInfo<AbstractField<T>> table,
                                                                   StateManager stateManager,
                                                                   Instant emittedAt) {
    final String streamName = airbyteStream.getStream().getName();
    final String namespace = airbyteStream.getStream().getNamespace();
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(streamName, namespace);
    final Set<String> selectedFieldsInCatalog = CatalogHelpers.getTopLevelFieldNames(airbyteStream);
    final List<String> selectedDatabaseFields = table.getFields()
        .stream()
        .map(AbstractField::getName)
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

      final JsonSchemaPrimitive cursorType = IncrementalUtils
          .getCursorType(airbyteStream, cursorField);

      iterator = AutoCloseableIterators.transform(autoCloseableIterator -> new StateDecoratingIterator(
          autoCloseableIterator,
          stateManager,
          pair,
          cursorField,
          cursorOptional.orElse(null),
          cursorType),
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

  private AutoCloseableIterator<AirbyteMessage> getIncrementalStream(K database,
                                                                     ConfiguredAirbyteStream airbyteStream,
                                                                     List<String> selectedDatabaseFields,
                                                                     TableInfo<AbstractField<T>> table,
                                                                     String cursor,
                                                                     Instant emittedAt) {
    final String streamName = airbyteStream.getStream().getName();
    final String namespace = airbyteStream.getStream().getNamespace();
    final String cursorField = IncrementalUtils.getCursorField(airbyteStream);
    final T cursorJdbcType = table.getFields().stream()
        .filter(info -> info.getName().equals(cursorField))
        .map(AbstractField::getType)
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
        cursorJdbcType,
        cursor);

    return getMessageIterator(queryIterator, streamName, namespace, emittedAt.toEpochMilli());
  }

  private AutoCloseableIterator<AirbyteMessage> getFullRefreshStream(K database,
                                                                     String streamName,
                                                                     String namespace,
                                                                     List<String> selectedDatabaseFields,
                                                                     TableInfo<AbstractField<T>> table,
                                                                     Instant emittedAt) {
    final AutoCloseableIterator<JsonNode> queryStream =
        queryTableFullRefresh(database, selectedDatabaseFields, table.getNameSpace(), table.getName());
    return getMessageIterator(queryStream, streamName, namespace, emittedAt.toEpochMilli());
  }

  protected abstract JsonSchemaPrimitive getType(T columnType);

  protected abstract String getFullyQualifiedTableName(String nameSpace, String tableName);

  private List<TableInfo<Field>> getTables(final K database) throws Exception {
    final List<TableInfo<AbstractField<T>>> tableInfos = discoverWithoutSystemTables(database);
    final Map<String, List<String>> fullyQualifiedTableNameToPrimaryKeys = discoverPrimaryKeys(database, tableInfos);

    return tableInfos.stream()
        .map(t -> {
          // some databases return multiple copies of the same record for a column (e.g. redshift) because
          // they have at least once delivery guarantees. we want to dedupe these, but first we check that the
          // records are actually the same and provide a good error message if they are not.
          assertColumnsWithSameNameAreSame(t.getNameSpace(), t.getName(), t.getFields());
          final List<Field> fields = t.getFields()
              .stream()
              .map(f -> Field.of(f.getName(), getType(f.getType())))
              .distinct()
              .collect(Collectors.toList());
          final String fullyQualifiedTableName = getFullyQualifiedTableName(t.getNameSpace(), t.getName());
          final List<String> primaryKeys = fullyQualifiedTableNameToPrimaryKeys.getOrDefault(fullyQualifiedTableName, Collections
              .emptyList());

          return TableInfo.<Field>builder().nameSpace(t.getNameSpace()).name(t.getName()).fields(fields).primaryKeys(primaryKeys)
              .build();
        })
        .collect(Collectors.toList());
  }

  /**
   * Discover Primary keys for each table and @return a map of schema.table name to their associated
   * list of primary key fields.
   *
   * When invoking the conn.getMetaData().getPrimaryKeys() function without a table name, it may fail
   * on some databases (for example MySql) but works on others (for instance Postgres). To avoid
   * making repeated queries to the DB, we try to get all primary keys without specifying a table
   * first, if it doesn't work, we retry one table at a time.
   */
  protected abstract Map<String, List<String>> discoverPrimaryKeys(K database,
                                                                   List<TableInfo<AbstractField<T>>> tableInfos);

  protected void assertColumnsWithSameNameAreSame(String nameSpace, String tableName, List<AbstractField<T>> columns) {
    columns.stream()
        .collect(Collectors.groupingBy(AbstractField<T>::getName))
        .values()
        .forEach(columnsWithSameName -> {
          final AbstractField<T> comparisonColumn = columnsWithSameName.get(0);
          columnsWithSameName.forEach(column -> {
            if (!column.equals(comparisonColumn)) {
              throw new RuntimeException(
                  String.format("Found multiple columns with same name: %s in table: %s.%s but the columns are not the same. columns: %s",
                      comparisonColumn.getName(), nameSpace, tableName, columns));
            }
          });
        });
  }

  protected List<TableInfo<AbstractField<T>>> discoverWithoutSystemTables(final K database) throws Exception {
    Set<String> systemNameSpaces = getExcludedInternalNameSpaces();
    List<TableInfo<AbstractField<T>>> discoveredTables = discoverInternal(database);
    return (systemNameSpaces == null || systemNameSpaces.isEmpty() ? discoveredTables
        : discoveredTables.stream().filter(table -> !systemNameSpaces.contains(table.getNameSpace())).collect(
            Collectors.toList()));
  }

  protected abstract List<TableInfo<AbstractField<T>>> discoverInternal(final K database)
      throws Exception;

  public AutoCloseableIterator<AirbyteMessage> getMessageIterator(AutoCloseableIterator<JsonNode> recordIterator,
                                                                  String streamName,
                                                                  String namespace,
                                                                  long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withNamespace(namespace)
            .withEmittedAt(emittedAt)
            .withData(r)));
  }

  protected abstract String getQuoteString();

  private String getIdentifierWithQuoting(String identifier) {
    return getQuoteString() + identifier + getQuoteString();
  }

  private String enquoteIdentifierList(List<String> identifiers) {
    final StringJoiner joiner = new StringJoiner(",");
    for (String identifier : identifiers) {
      joiner.add(getIdentifierWithQuoting(identifier));
    }
    return joiner.toString();
  }

  private String getFullTableName(String nameSpace, String tableName) {
    return (nameSpace == null || nameSpace.isEmpty() ? getIdentifierWithQuoting(tableName)
        : getIdentifierWithQuoting(nameSpace) + "." + getIdentifierWithQuoting(tableName));
  }

  protected AutoCloseableIterator<JsonNode> queryTable(K database, String sqlQuery) {
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.query(sqlQuery);
        return AutoCloseableIterators.fromStream(stream);
      } catch (SQLException e) {
        throw new RuntimeException(e);
      }
    });
  }

  public AutoCloseableIterator<JsonNode> queryTableFullRefresh(K database,
                                                               List<String> columnNames,
                                                               String schemaName,
                                                               String tableName) {
    LOGGER.info("Queueing query for table: {}", tableName);
    return queryTable(database, String.format("SELECT %s FROM %s",
        enquoteIdentifierList(columnNames),
        getFullTableName(schemaName, tableName)));
  }

  public abstract AutoCloseableIterator<JsonNode> queryTableIncremental(K database,
                                                                        List<String> columnNames,
                                                                        String schemaName,
                                                                        String tableName,
                                                                        String cursorField,
                                                                        T cursorFieldType,
                                                                        String cursor);

  private K createDatabaseInternal(JsonNode sourceConfig) throws Exception {
    K database = createDatabase(sourceConfig);
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(toDatabaseConfig(sourceConfig));
    return database;
  }

  protected abstract K createDatabase(JsonNode config) throws Exception;

}
