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

package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.models.JdbcState;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.AbstractMap.SimpleImmutableEntry;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractJdbcSource extends BaseConnector implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcSource.class);

  private static final String JDBC_COLUMN_DATABASE_NAME = "TABLE_CAT";
  private static final String JDBC_COLUMN_SCHEMA_NAME = "TABLE_SCHEM";
  private static final String JDBC_COLUMN_TABLE_NAME = "TABLE_NAME";
  private static final String JDBC_COLUMN_COLUMN_NAME = "COLUMN_NAME";
  private static final String JDBC_COLUMN_DATA_TYPE = "DATA_TYPE";

  private static final String INTERNAL_SCHEMA_NAME = "schemaName";
  private static final String INTERNAL_TABLE_NAME = "tableName";
  private static final String INTERNAL_COLUMN_NAME = "columnName";
  private static final String INTERNAL_COLUMN_TYPE = "columnType";

  private final String driverClass;
  private final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration;

  public AbstractJdbcSource(final String driverClass, final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration) {
    this.driverClass = driverClass;
    this.jdbcStreamingQueryConfiguration = jdbcStreamingQueryConfiguration;
  }

  /**
   * Map a database implementation-specific configuration to json object that adheres to the
   * AbstractJdbcSource config spec. See resources/spec.json.
   *
   * @param config database implementation-specific configuration.
   * @return jdbc spec.
   */
  public abstract JsonNode toJdbcConfig(JsonNode config);

  /**
   * Set of schemas that are internal to the database (e.g. system schemas) and should not be included
   * in the catalog.
   *
   * @return set of schemas to be ignored.
   */
  public abstract Set<String> getExcludedInternalSchemas();

  @Override
  public AirbyteConnectionStatus check(JsonNode config) {
    try (final JdbcDatabase database = createDatabase(config)) {
      // attempt to get metadata from the database as a cheap way of seeing if we can connect.
      database.bufferedResultSetQuery(conn -> conn.getMetaData().getCatalogs(), JdbcUtils::rowToJson);

      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED);
    } catch (Exception e) {
      LOGGER.debug("Exception while checking connection: ", e);
      return new AirbyteConnectionStatus()
          .withStatus(Status.FAILED)
          .withMessage("Could not connect with provided configuration.");
    }
  }

  @Override
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    try (final JdbcDatabase database = createDatabase(config)) {
      return new AirbyteCatalog()
          .withStreams(getTables(
              database,
              Optional.ofNullable(config.get("database")).map(JsonNode::asText),
              Optional.ofNullable(config.get("schema")).map(JsonNode::asText))
                  .stream()
                  .map(t -> CatalogHelpers.createAirbyteStream(t.getName(), t.getFields())
                      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
                      .withSourceDefinedPrimaryKey(t.getPrimaryKeys()
                          .stream()
                          .filter(Objects::nonNull)
                          .map(Collections::singletonList)
                          .collect(Collectors.toList())))
                  .collect(Collectors.toList()));
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(JsonNode config, ConfiguredAirbyteCatalog catalog, JsonNode state) throws Exception {
    final JdbcStateManager stateManager =
        new JdbcStateManager(state == null ? JdbcStateManager.emptyState() : Jsons.object(state, JdbcState.class), catalog);
    final Instant emittedAt = Instant.now();

    final JdbcDatabase database = createDatabase(config);

    final Map<String, TableInfoInternal> tableNameToTable = discoverInternal(
        database,
        Optional.ofNullable(config.get("database")).map(JsonNode::asText),
        Optional.ofNullable(config.get("schema")).map(JsonNode::asText))
            .stream()
            .collect(Collectors.toMap(t -> String.format("%s.%s", t.getSchemaName(), t.getName()), Function.identity()));

    final List<AutoCloseableIterator<AirbyteMessage>> incrementalIterators =
        getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
    final List<AutoCloseableIterator<AirbyteMessage>> fullRefreshIterators =
        getFullRefreshIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = Stream.of(incrementalIterators, fullRefreshIterators)
        .flatMap(Collection::stream)
        .collect(Collectors.toList());

    return AutoCloseableIterators.appendOnClose(AutoCloseableIterators.concatWithEagerClose(iteratorList), () -> {
      LOGGER.info("Closing database connection pool.");
      Exceptions.toRuntime(database::close);
      LOGGER.info("Closed database connection pool.");
    });
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(JdbcDatabase database,
                                                                             ConfiguredAirbyteCatalog catalog,
                                                                             Map<String, TableInfoInternal> tableNameToTable,
                                                                             JdbcStateManager stateManager,
                                                                             Instant emittedAt) {
    return getSelectedIterators(
        database,
        catalog,
        tableNameToTable,
        stateManager,
        emittedAt,
        configuredStream -> configuredStream.getSyncMode().equals(SyncMode.INCREMENTAL));
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getFullRefreshIterators(JdbcDatabase database,
                                                                             ConfiguredAirbyteCatalog catalog,
                                                                             Map<String, TableInfoInternal> tableNameToTable,
                                                                             JdbcStateManager stateManager,
                                                                             Instant emittedAt) {
    return getSelectedIterators(
        database,
        catalog,
        tableNameToTable,
        stateManager,
        emittedAt,
        configuredStream -> configuredStream.getSyncMode().equals(SyncMode.FULL_REFRESH));
  }

  private List<AutoCloseableIterator<AirbyteMessage>> getSelectedIterators(JdbcDatabase database,
                                                                           ConfiguredAirbyteCatalog catalog,
                                                                           Map<String, TableInfoInternal> tableNameToTable,
                                                                           JdbcStateManager stateManager,
                                                                           Instant emittedAt,
                                                                           Predicate<ConfiguredAirbyteStream> selector) {
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = new ArrayList<>();

    for (final ConfiguredAirbyteStream airbyteStream : catalog.getStreams()) {
      if (selector.test(airbyteStream)) {
        final String streamName = airbyteStream.getStream().getName();
        if (!tableNameToTable.containsKey(streamName)) {
          LOGGER.info("Skipping stream {} because it is not in the source", streamName);
          continue;
        }

        final TableInfoInternal table = tableNameToTable.get(streamName);
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

  private AutoCloseableIterator<AirbyteMessage> createReadIterator(JdbcDatabase database,
                                                                   ConfiguredAirbyteStream airbyteStream,
                                                                   TableInfoInternal table,
                                                                   JdbcStateManager stateManager,
                                                                   Instant emittedAt) {
    final String streamName = airbyteStream.getStream().getName();
    final Set<String> selectedFieldsInCatalog = CatalogHelpers.getTopLevelFieldNames(airbyteStream);
    final List<String> selectedDatabaseFields = table.getFields()
        .stream()
        .map(ColumnInfo::getColumnName)
        .filter(selectedFieldsInCatalog::contains)
        .collect(Collectors.toList());

    final AutoCloseableIterator<AirbyteMessage> iterator;
    if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
      final String cursorField = IncrementalUtils.getCursorField(airbyteStream);
      final Optional<String> cursorOptional = stateManager.getCursor(streamName);

      final AutoCloseableIterator<AirbyteMessage> airbyteMessageIterator;
      if (cursorOptional.isPresent()) {
        airbyteMessageIterator = getIncrementalStream(database, airbyteStream, selectedDatabaseFields, table, cursorOptional.get(), emittedAt);
      } else {
        // if no cursor is present then this is the first read for is the same as doing a full refresh read.
        airbyteMessageIterator = getFullRefreshStream(database, streamName, selectedDatabaseFields, table, emittedAt);
      }

      final JsonSchemaPrimitive cursorType = IncrementalUtils.getCursorType(airbyteStream, cursorField);

      iterator = AutoCloseableIterators.transform(autoCloseableIterator -> new StateDecoratingIterator(
          autoCloseableIterator,
          stateManager,
          streamName,
          cursorField,
          cursorOptional.orElse(null),
          cursorType),
          airbyteMessageIterator);
    } else if (airbyteStream.getSyncMode() == SyncMode.FULL_REFRESH) {
      iterator = getFullRefreshStream(database, streamName, selectedDatabaseFields, table, emittedAt);
    } else if (airbyteStream.getSyncMode() == null) {
      throw new IllegalArgumentException(String.format("%s requires a source sync mode", AbstractJdbcSource.class));
    } else {
      throw new IllegalArgumentException(String.format("%s does not support sync mode: %s.", AbstractJdbcSource.class, airbyteStream.getSyncMode()));
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

  private static AutoCloseableIterator<AirbyteMessage> getIncrementalStream(JdbcDatabase database,
                                                                            ConfiguredAirbyteStream airbyteStream,
                                                                            List<String> selectedDatabaseFields,
                                                                            TableInfoInternal table,
                                                                            String cursor,
                                                                            Instant emittedAt) {
    final String streamName = airbyteStream.getStream().getName();
    final String cursorField = IncrementalUtils.getCursorField(airbyteStream);
    final JDBCType cursorJdbcType = table.getFields().stream()
        .filter(info -> info.getColumnName().equals(cursorField))
        .map(ColumnInfo::getColumnType)
        .findFirst()
        .orElseThrow();

    Preconditions.checkState(table.getFields().stream().anyMatch(f -> f.getColumnName().equals(cursorField)),
        String.format("Could not find cursor field %s in table %s", cursorField, table.getName()));

    final AutoCloseableIterator<JsonNode> queryIterator = queryTableIncremental(
        database,
        selectedDatabaseFields,
        table.getSchemaName(),
        table.getName(),
        cursorField,
        cursorJdbcType,
        cursor);

    return getMessageIterator(queryIterator, streamName, emittedAt.toEpochMilli());
  }

  private static AutoCloseableIterator<AirbyteMessage> getFullRefreshStream(JdbcDatabase database,
                                                                            String streamName,
                                                                            List<String> selectedDatabaseFields,
                                                                            TableInfoInternal table,
                                                                            Instant emittedAt) {
    final AutoCloseableIterator<JsonNode> queryStream =
        queryTableFullRefresh(database, selectedDatabaseFields, table.getSchemaName(), table.getName());
    return getMessageIterator(queryStream, streamName, emittedAt.toEpochMilli());
  }

  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  private List<TableInfo> getTables(final JdbcDatabase database,
                                    final Optional<String> databaseOptional,
                                    final Optional<String> schemaOptional)
      throws Exception {
    final List<TableInfoInternal> tableInfos = discoverInternal(database, databaseOptional, schemaOptional);
    final Map<String, List<String>> tablePrimaryKeys = discoverPrimaryKeys(database, databaseOptional, schemaOptional, tableInfos);
    return tableInfos.stream()
        .map(t -> {
          // some databases return multiple copies of the same record for a column (e.g. redshift) because
          // they have at least once delivery guarantees. we want to dedupe these, but first we check that the
          // records are actually the same and provide a good error message if they are not.
          assertColumnsWithSameNameAreSame(t.getSchemaName(), t.getName(), t.getFields());
          final List<Field> fields = t.getFields()
              .stream()
              .map(f -> Field.of(f.getColumnName(), JdbcUtils.getType(f.getColumnType())))
              .distinct()
              .collect(Collectors.toList());
          final String streamName = JdbcUtils.getFullyQualifiedTableName(t.getSchemaName(), t.getName());
          final List<String> primaryKeys = tablePrimaryKeys.getOrDefault(streamName, Collections.emptyList());
          return new TableInfo(streamName, fields, primaryKeys);
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
  private Map<String, List<String>> discoverPrimaryKeys(JdbcDatabase database,
                                                        Optional<String> databaseOptional,
                                                        Optional<String> schemaOptional,
                                                        List<TableInfoInternal> tableInfos) {
    try {
      // Get all primary keys without specifying a table name
      final Map<String, List<String>> tablePrimaryKeys = aggregatePrimateKeys(database.bufferedResultSetQuery(
          conn -> conn.getMetaData().getPrimaryKeys(databaseOptional.orElse(null), schemaOptional.orElse(null), null),
          r -> {
            final String schemaName =
                r.getObject(JDBC_COLUMN_SCHEMA_NAME) != null ? r.getString(JDBC_COLUMN_SCHEMA_NAME) : r.getString(JDBC_COLUMN_DATABASE_NAME);
            final String streamName = JdbcUtils.getFullyQualifiedTableName(schemaName, r.getString(JDBC_COLUMN_TABLE_NAME));
            final String primaryKey = r.getString(JDBC_COLUMN_COLUMN_NAME);
            return new SimpleImmutableEntry<>(streamName, primaryKey);
          }));
      if (!tablePrimaryKeys.isEmpty()) {
        return tablePrimaryKeys;
      }
    } catch (SQLException e) {
      LOGGER.debug(String.format("Could not retrieve primary keys without a table name (%s), retrying", e));
    }
    // Get primary keys one table at a time
    return tableInfos.stream()
        .collect(Collectors.toMap(
            tableInfo -> JdbcUtils.getFullyQualifiedTableName(tableInfo.getSchemaName(), tableInfo.getName()),
            tableInfo -> {
              final String streamName = JdbcUtils.getFullyQualifiedTableName(tableInfo.getSchemaName(), tableInfo.getName());
              try {
                final Map<String, List<String>> primaryKeys = aggregatePrimateKeys(database.bufferedResultSetQuery(
                    conn -> conn.getMetaData().getPrimaryKeys(databaseOptional.orElse(null), tableInfo.getSchemaName(), tableInfo.getName()),
                    r -> new SimpleImmutableEntry<>(streamName, r.getString(JDBC_COLUMN_COLUMN_NAME))));
                return primaryKeys.getOrDefault(streamName, Collections.emptyList());
              } catch (SQLException e) {
                LOGGER.error(String.format("Could not retrieve primary keys for %s: %s", streamName, e));
                return Collections.emptyList();
              }
            }));
  }

  /**
   * Aggregate list of @param entries of StreamName and PrimaryKey and
   *
   * @return a map by StreamName to associated list of primary keys
   */
  private static Map<String, List<String>> aggregatePrimateKeys(List<SimpleImmutableEntry<String, String>> entries) {
    final Map<String, List<String>> result = new HashMap<>();
    entries.forEach(entry -> {
      if (!result.containsKey(entry.getKey())) {
        result.put(entry.getKey(), new ArrayList<>());
      }
      result.get(entry.getKey()).add(entry.getValue());
    });
    return result;
  }

  private static void assertColumnsWithSameNameAreSame(String schemaName, String tableName, List<ColumnInfo> columns) {
    columns.stream()
        .collect(Collectors.groupingBy(ColumnInfo::getColumnName))
        .values()
        .forEach(columnsWithSameName -> {
          final ColumnInfo comparisonColumn = columnsWithSameName.get(0);
          columnsWithSameName.forEach(column -> {
            if (!column.equals(comparisonColumn)) {
              throw new RuntimeException(
                  String.format("Found multiple columns with same name: %s in table: %s.%s but the columns are not the same. columns: %s",
                      comparisonColumn.getColumnName(), schemaName, tableName, columns));
            }
          });
        });
  }

  @SuppressWarnings("OptionalUsedAsFieldOrParameterType")
  private List<TableInfoInternal> discoverInternal(final JdbcDatabase database,
                                                   final Optional<String> databaseOptional,
                                                   final Optional<String> schemaOptional)
      throws Exception {
    final Set<String> internalSchemas = new HashSet<>(getExcludedInternalSchemas());
    return database.bufferedResultSetQuery(
        conn -> conn.getMetaData().getColumns(databaseOptional.orElse(null), schemaOptional.orElse(null), null, null),
        resultSet -> Jsons.jsonNode(ImmutableMap.<String, Object>builder()
            // we always want a namespace, if we cannot get a schema, use db name.
            .put(INTERNAL_SCHEMA_NAME,
                resultSet.getObject(JDBC_COLUMN_SCHEMA_NAME) != null ? resultSet.getString(JDBC_COLUMN_SCHEMA_NAME)
                    : resultSet.getObject(JDBC_COLUMN_DATABASE_NAME))
            .put(INTERNAL_TABLE_NAME, resultSet.getString(JDBC_COLUMN_TABLE_NAME))
            .put(INTERNAL_COLUMN_NAME, resultSet.getString(JDBC_COLUMN_COLUMN_NAME))
            .put(INTERNAL_COLUMN_TYPE, resultSet.getString(JDBC_COLUMN_DATA_TYPE))
            .build()))
        .stream()
        .filter(t -> !internalSchemas.contains(t.get(INTERNAL_SCHEMA_NAME).asText()))
        // group by schema and table name to handle the case where a table with the same name exists in
        // multiple schemas.
        .collect(Collectors.groupingBy(t -> ImmutablePair.of(t.get(INTERNAL_SCHEMA_NAME).asText(), t.get(INTERNAL_TABLE_NAME).asText())))
        .values()
        .stream()
        .map(fields -> new TableInfoInternal(
            fields.get(0).get(INTERNAL_SCHEMA_NAME).asText(),
            fields.get(0).get(INTERNAL_TABLE_NAME).asText(),
            fields.stream()
                .map(f -> {
                  JDBCType jdbcType;
                  try {
                    jdbcType = JDBCType.valueOf(f.get(INTERNAL_COLUMN_TYPE).asInt());
                  } catch (IllegalArgumentException ex) {
                    LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
                        f.get(INTERNAL_COLUMN_NAME),
                        f.get(INTERNAL_SCHEMA_NAME),
                        f.get(INTERNAL_TABLE_NAME),
                        f.get(INTERNAL_COLUMN_TYPE)));
                    jdbcType = JDBCType.VARCHAR;
                  }
                  return new ColumnInfo(f.get(INTERNAL_COLUMN_NAME).asText(), jdbcType);
                })
                .collect(Collectors.toList())))
        .collect(Collectors.toList());
  }

  private static AutoCloseableIterator<AirbyteMessage> getMessageIterator(AutoCloseableIterator<JsonNode> recordIterator,
                                                                          String streamName,
                                                                          long emittedAt) {
    return AutoCloseableIterators.transform(recordIterator, r -> new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(streamName)
            .withEmittedAt(emittedAt)
            .withData(r)));
  }

  public static AutoCloseableIterator<JsonNode> queryTableFullRefresh(JdbcDatabase database,
                                                                      List<String> columnNames,
                                                                      String schemaName,
                                                                      String tableName) {
    LOGGER.info("Queueing query for table: {}", tableName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.query(
            connection -> {
              LOGGER.info("Preparing query for table: {}", tableName);
              final String sql = String.format("SELECT %s FROM %s",
                  JdbcUtils.enquoteIdentifierList(connection, columnNames),
                  JdbcUtils.getFullyQualifiedTableNameWithQuoting(connection, schemaName, tableName));
              final PreparedStatement preparedStatement = connection.prepareStatement(sql);
              LOGGER.info("Executing query for table: {}", tableName);
              return preparedStatement;
            },
            JdbcUtils::rowToJson);
        return AutoCloseableIterators.fromStream(stream);
      } catch (SQLException e) {
        throw new RuntimeException(e);
      }
    });
  }

  public static AutoCloseableIterator<JsonNode> queryTableIncremental(JdbcDatabase database,
                                                                      List<String> columnNames,
                                                                      String schemaName,
                                                                      String tableName,
                                                                      String cursorField,
                                                                      JDBCType cursorFieldType,
                                                                      String cursor) {

    LOGGER.info("Queueing query for table: {}", tableName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.query(
            connection -> {
              LOGGER.info("Preparing query for table: {}", tableName);
              final String sql = String.format("SELECT %s FROM %s WHERE %s > ?",
                  JdbcUtils.enquoteIdentifierList(connection, columnNames),
                  JdbcUtils.getFullyQualifiedTableNameWithQuoting(connection, schemaName, tableName),
                  JdbcUtils.enquoteIdentifier(connection, cursorField));

              final PreparedStatement preparedStatement = connection.prepareStatement(sql);
              JdbcUtils.setStatementField(preparedStatement, 1, cursorFieldType, cursor);
              LOGGER.info("Executing query for table: {}", tableName);
              return preparedStatement;
            },
            JdbcUtils::rowToJson);
        return AutoCloseableIterators.fromStream(stream);
      } catch (SQLException e) {
        throw new RuntimeException(e);
      }
    });
  }

  private JdbcDatabase createDatabase(JsonNode config) {
    final JsonNode jdbcConfig = toJdbcConfig(config);

    return Databases.createStreamingJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        driverClass,
        jdbcStreamingQueryConfiguration);
  }

  protected static class TableInfo {

    private final String name;
    private final List<Field> fields;
    private final List<String> primaryKeys;

    public TableInfo(String name, List<Field> fields, List<String> primaryKeys) {
      this.name = name;
      this.fields = fields;
      this.primaryKeys = primaryKeys;
    }

    public String getName() {
      return name;
    }

    public List<Field> getFields() {
      return fields;
    }

    public List<String> getPrimaryKeys() {
      return primaryKeys;
    }

  }

  protected static class TableInfoInternal {

    private final String schemaName;
    private final String name;
    private final List<ColumnInfo> fields;

    public TableInfoInternal(String schemaName, String tableName, List<ColumnInfo> fields) {
      this.schemaName = schemaName;
      this.name = tableName;
      this.fields = fields;
    }

    public String getSchemaName() {
      return schemaName;
    }

    public String getName() {
      return name;
    }

    public List<ColumnInfo> getFields() {
      return fields;
    }

  }

  protected static class ColumnInfo {

    private final String columnName;
    private final JDBCType columnType;

    public ColumnInfo(String columnName, JDBCType columnType) {
      this.columnName = columnName;
      this.columnType = columnType;
    }

    public String getColumnName() {
      return columnName;
    }

    public JDBCType getColumnType() {
      return columnType;
    }

    @Override
    public boolean equals(Object o) {
      if (this == o) {
        return true;
      }
      if (o == null || getClass() != o.getClass()) {
        return false;
      }
      ColumnInfo that = (ColumnInfo) o;
      return Objects.equals(columnName, that.columnName) && columnType == that.columnType;
    }

    @Override
    public int hashCode() {
      return Objects.hash(columnName, columnType);
    }

    @Override
    public String toString() {
      return "ColumnInfo{" +
          "columnName='" + columnName + '\'' +
          ", columnType=" + columnType +
          '}';
    }

  }

}
