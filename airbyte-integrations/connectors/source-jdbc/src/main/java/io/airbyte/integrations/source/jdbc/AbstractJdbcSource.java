/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_SIZE;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_COLUMN_COLUMN_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_COLUMN_DATABASE_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_COLUMN_DATA_TYPE;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_COLUMN_SCHEMA_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_COLUMN_SIZE;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_COLUMN_TABLE_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_COLUMN_TYPE_NAME;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.JdbcCompatibleSourceOperations;
import io.airbyte.db.SqlDatabase;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.db.jdbc.streaming.JdbcStreamingQueryConfig;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.integrations.source.relationaldb.AbstractRelationalDbSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.AbstractMap.SimpleImmutableEntry;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class contains helper functions and boilerplate for implementing a source connector for a
 * relational DB source which can be accessed via JDBC driver. If you are implementing a connector
 * for a relational DB which has a JDBC driver, make an effort to use this class.
 */
public abstract class AbstractJdbcSource<Datatype> extends AbstractRelationalDbSource<Datatype, JdbcDatabase> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcSource.class);

  protected final String driverClass;
  protected final Supplier<JdbcStreamingQueryConfig> streamingQueryConfigProvider;
  protected final JdbcCompatibleSourceOperations<Datatype> sourceOperations;

  protected String quoteString;

  public AbstractJdbcSource(final String driverClass,
                            final Supplier<JdbcStreamingQueryConfig> streamingQueryConfigProvider,
                            final JdbcCompatibleSourceOperations<Datatype> sourceOperations) {
    this.driverClass = driverClass;
    this.streamingQueryConfigProvider = streamingQueryConfigProvider;
    this.sourceOperations = sourceOperations;
  }

  /**
   * Configures a list of operations that can be used to check the connection to the source.
   *
   * @return list of consumers that run queries for the check command.
   */
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config) throws Exception {
    return ImmutableList.of(database -> {
      LOGGER.info("Attempting to get metadata from the database to see if we can connect.");
      database.bufferedResultSetQuery(conn -> conn.getMetaData().getCatalogs(), sourceOperations::rowToJson);
    });
  }

  /**
   * Aggregate list of @param entries of StreamName and PrimaryKey and
   *
   * @return a map by StreamName to associated list of primary keys
   */
  private static Map<String, List<String>> aggregatePrimateKeys(final List<SimpleImmutableEntry<String, String>> entries) {
    final Map<String, List<String>> result = new HashMap<>();
    entries.forEach(entry -> {
      if (!result.containsKey(entry.getKey())) {
        result.put(entry.getKey(), new ArrayList<>());
      }
      result.get(entry.getKey()).add(entry.getValue());
    });
    return result;
  }

  private String getCatalog(final SqlDatabase database) {
    return (database.getSourceConfig().has("database") ? database.getSourceConfig().get("database").asText() : null);
  }

  @Override
  protected List<TableInfo<CommonField<Datatype>>> discoverInternal(final JdbcDatabase database, final String schema) throws Exception {
    final Set<String> internalSchemas = new HashSet<>(getExcludedInternalNameSpaces());
    LOGGER.info("Internal schemas to exclude: {}", internalSchemas);
    final Set<JdbcPrivilegeDto> tablesWithSelectGrantPrivilege = getPrivilegesTableForCurrentUser(database, schema);
    return database.bufferedResultSetQuery(
        // retrieve column metadata from the database
        conn -> conn.getMetaData().getColumns(getCatalog(database), schema, null, null),
        // store essential column metadata to a Json object from the result set about each column
        this::getColumnMetadata)
        .stream()
        .filter(excludeNotAccessibleTables(internalSchemas, tablesWithSelectGrantPrivilege))
        // group by schema and table name to handle the case where a table with the same name exists in
        // multiple schemas.
        .collect(Collectors.groupingBy(t -> ImmutablePair.of(t.get(INTERNAL_SCHEMA_NAME).asText(), t.get(INTERNAL_TABLE_NAME).asText())))
        .values()
        .stream()
        .map(fields -> TableInfo.<CommonField<Datatype>>builder()
            .nameSpace(fields.get(0).get(INTERNAL_SCHEMA_NAME).asText())
            .name(fields.get(0).get(INTERNAL_TABLE_NAME).asText())
            .fields(fields.stream()
                // read the column metadata Json object, and determine its type
                .map(f -> {
                  final Datatype datatype = getFieldType(f);
                  final JsonSchemaType jsonType = getType(datatype);
                  LOGGER.info("Table {} column {} (type {}[{}]) -> {}",
                      fields.get(0).get(INTERNAL_TABLE_NAME).asText(),
                      f.get(INTERNAL_COLUMN_NAME).asText(),
                      f.get(INTERNAL_COLUMN_TYPE_NAME).asText(),
                      f.get(INTERNAL_COLUMN_SIZE).asInt(),
                      jsonType);
                  return new CommonField<Datatype>(f.get(INTERNAL_COLUMN_NAME).asText(), datatype) {};
                })
                .collect(Collectors.toList()))
            .build())
        .collect(Collectors.toList());
  }

  protected Predicate<JsonNode> excludeNotAccessibleTables(final Set<String> internalSchemas,
                                                           final Set<JdbcPrivilegeDto> tablesWithSelectGrantPrivilege) {
    return jsonNode -> {
      if (tablesWithSelectGrantPrivilege.isEmpty()) {
        return isNotInternalSchema(jsonNode, internalSchemas);
      }
      return tablesWithSelectGrantPrivilege.stream()
          .anyMatch(e -> e.getSchemaName().equals(jsonNode.get(INTERNAL_SCHEMA_NAME).asText()))
          && tablesWithSelectGrantPrivilege.stream()
              .anyMatch(e -> e.getTableName().equals(jsonNode.get(INTERNAL_TABLE_NAME).asText()))
          && !internalSchemas.contains(jsonNode.get(INTERNAL_SCHEMA_NAME).asText());
    };
  }

  // needs to override isNotInternalSchema for connectors that override
  // getPrivilegesTableForCurrentUser()
  protected boolean isNotInternalSchema(final JsonNode jsonNode, final Set<String> internalSchemas) {
    return !internalSchemas.contains(jsonNode.get(INTERNAL_SCHEMA_NAME).asText());
  }

  /**
   * @param resultSet Description of a column available in the table catalog.
   * @return Essential information about a column to determine which table it belongs to and its type.
   */
  private JsonNode getColumnMetadata(final ResultSet resultSet) throws SQLException {
    return Jsons.jsonNode(ImmutableMap.<String, Object>builder()
        // we always want a namespace, if we cannot get a schema, use db name.
        .put(INTERNAL_SCHEMA_NAME,
            resultSet.getObject(JDBC_COLUMN_SCHEMA_NAME) != null ? resultSet.getString(JDBC_COLUMN_SCHEMA_NAME)
                : resultSet.getObject(JDBC_COLUMN_DATABASE_NAME))
        .put(INTERNAL_TABLE_NAME, resultSet.getString(JDBC_COLUMN_TABLE_NAME))
        .put(INTERNAL_COLUMN_NAME, resultSet.getString(JDBC_COLUMN_COLUMN_NAME))
        .put(INTERNAL_COLUMN_TYPE, resultSet.getString(JDBC_COLUMN_DATA_TYPE))
        .put(INTERNAL_COLUMN_TYPE_NAME, resultSet.getString(JDBC_COLUMN_TYPE_NAME))
        .put(INTERNAL_COLUMN_SIZE, resultSet.getInt(JDBC_COLUMN_SIZE))
        .build());
  }

  /**
   * @param field Essential column information returned from
   *        {@link AbstractJdbcSource#getColumnMetadata}.
   */
  public Datatype getFieldType(final JsonNode field) {
    return sourceOperations.getFieldType(field);
  }

  @Override
  public List<TableInfo<CommonField<Datatype>>> discoverInternal(final JdbcDatabase database)
      throws Exception {
    return discoverInternal(database, null);
  }

  @Override
  public JsonSchemaType getType(final Datatype columnType) {
    return sourceOperations.getJsonType(columnType);
  }

  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(final JdbcDatabase database,
                                                          final List<TableInfo<CommonField<Datatype>>> tableInfos) {
    LOGGER.info("Discover primary keys for tables: " + tableInfos.stream().map(TableInfo::getName).collect(
        Collectors.toSet()));
    try {
      // Get all primary keys without specifying a table name
      final Map<String, List<String>> tablePrimaryKeys = aggregatePrimateKeys(database.bufferedResultSetQuery(
          conn -> conn.getMetaData().getPrimaryKeys(getCatalog(database), null, null),
          r -> {
            final String schemaName =
                r.getObject(JDBC_COLUMN_SCHEMA_NAME) != null ? r.getString(JDBC_COLUMN_SCHEMA_NAME) : r.getString(JDBC_COLUMN_DATABASE_NAME);
            final String streamName = sourceOperations.getFullyQualifiedTableName(schemaName, r.getString(JDBC_COLUMN_TABLE_NAME));
            final String primaryKey = r.getString(JDBC_COLUMN_COLUMN_NAME);
            return new SimpleImmutableEntry<>(streamName, primaryKey);
          }));
      if (!tablePrimaryKeys.isEmpty()) {
        return tablePrimaryKeys;
      }
    } catch (final SQLException e) {
      LOGGER.debug(String.format("Could not retrieve primary keys without a table name (%s), retrying", e));
    }
    // Get primary keys one table at a time
    return tableInfos.stream()
        .collect(Collectors.toMap(
            tableInfo -> sourceOperations
                .getFullyQualifiedTableName(tableInfo.getNameSpace(), tableInfo.getName()),
            tableInfo -> {
              final String streamName = sourceOperations
                  .getFullyQualifiedTableName(tableInfo.getNameSpace(), tableInfo.getName());
              try {
                final Map<String, List<String>> primaryKeys = aggregatePrimateKeys(database.bufferedResultSetQuery(
                    conn -> conn.getMetaData().getPrimaryKeys(getCatalog(database), tableInfo.getNameSpace(), tableInfo.getName()),
                    r -> new SimpleImmutableEntry<>(streamName, r.getString(JDBC_COLUMN_COLUMN_NAME))));
                return primaryKeys.getOrDefault(streamName, Collections.emptyList());
              } catch (final SQLException e) {
                LOGGER.error(String.format("Could not retrieve primary keys for %s: %s", streamName, e));
                return Collections.emptyList();
              }
            }));
  }

  @Override
  protected String getQuoteString() {
    return quoteString;
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableIncremental(final JdbcDatabase database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final String cursorField,
                                                               final Datatype cursorFieldType,
                                                               final String cursor) {
    LOGGER.info("Queueing query for table: {}", tableName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.unsafeQuery(
            connection -> {
              LOGGER.info("Preparing query for table: {}", tableName);
              final String sql = String.format("SELECT %s FROM %s WHERE %s > ?",
                  sourceOperations.enquoteIdentifierList(connection, columnNames),
                  sourceOperations
                      .getFullyQualifiedTableNameWithQuoting(connection, schemaName, tableName),
                  sourceOperations.enquoteIdentifier(connection, cursorField));

              final PreparedStatement preparedStatement = connection.prepareStatement(sql);
              sourceOperations.setStatementField(preparedStatement, 1, cursorFieldType, cursor);
              LOGGER.info("Executing query for table: {}", tableName);
              return preparedStatement;
            },
            sourceOperations::rowToJson);
        return AutoCloseableIterators.fromStream(stream);
      } catch (final SQLException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public JdbcDatabase createDatabase(final JsonNode config) throws SQLException {
    final JsonNode jdbcConfig = toDatabaseConfig(config);
    final JdbcDatabase database = new StreamingJdbcDatabase(
        DataSourceFactory.create(
            jdbcConfig.has("username") ? jdbcConfig.get("username").asText() : null,
            jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
            driverClass,
            jdbcConfig.get("jdbc_url").asText(),
            JdbcUtils.parseJdbcParameters(jdbcConfig, "connection_properties", getJdbcParameterDelimiter())
        ),
        sourceOperations,
        streamingQueryConfigProvider
    );

    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);

    return database;
  }

  protected String getJdbcParameterDelimiter() {
    return "&";
  }

}
