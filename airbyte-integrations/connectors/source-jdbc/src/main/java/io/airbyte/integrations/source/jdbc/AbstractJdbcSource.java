/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Databases;
import io.airbyte.db.SqlDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.AbstractRelationalDbSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.AbstractMap.SimpleImmutableEntry;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
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
public abstract class AbstractJdbcSource extends AbstractRelationalDbSource<JDBCType, JdbcDatabase> implements Source {

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
  protected final JdbcSourceOperations sourceOperations;

  private String quoteString;

  public AbstractJdbcSource(final String driverClass, final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration) {
    this(driverClass, jdbcStreamingQueryConfiguration, JdbcUtils.getDefaultSourceOperations());
  }

  public AbstractJdbcSource(final String driverClass,
                            final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration,
                            final JdbcSourceOperations sourceOperations) {
    this.driverClass = driverClass;
    this.jdbcStreamingQueryConfiguration = jdbcStreamingQueryConfiguration;
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
  protected List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database, final String schema) throws Exception {
    final Set<String> internalSchemas = new HashSet<>(getExcludedInternalNameSpaces());
    return database.bufferedResultSetQuery(
        conn -> conn.getMetaData().getColumns(getCatalog(database), schema, null, null),
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
        .map(fields -> TableInfo.<CommonField<JDBCType>>builder()
            .nameSpace(fields.get(0).get(INTERNAL_SCHEMA_NAME).asText())
            .name(fields.get(0).get(INTERNAL_TABLE_NAME).asText())
            .fields(fields.stream()
                .map(f -> {
                  JDBCType jdbcType;
                  try {
                    jdbcType = JDBCType.valueOf(f.get(INTERNAL_COLUMN_TYPE).asInt());
                  } catch (final IllegalArgumentException ex) {
                    LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
                        f.get(INTERNAL_COLUMN_NAME),
                        f.get(INTERNAL_SCHEMA_NAME),
                        f.get(INTERNAL_TABLE_NAME),
                        f.get(INTERNAL_COLUMN_TYPE)));
                    jdbcType = JDBCType.VARCHAR;
                  }
                  return new CommonField<JDBCType>(f.get(INTERNAL_COLUMN_NAME).asText(), jdbcType) {};
                })
                .collect(Collectors.toList()))
            .build())
        .collect(Collectors.toList());
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database)
      throws Exception {
    return discoverInternal(database, null);
  }

  @Override
  protected JsonSchemaPrimitive getType(final JDBCType columnType) {
    return sourceOperations.getType(columnType);
  }

  @Override
  protected Map<String, List<String>> discoverPrimaryKeys(final JdbcDatabase database,
                                                          final List<TableInfo<CommonField<JDBCType>>> tableInfos) {
    LOGGER.info("Discover primary keys for tables: " + tableInfos.stream().map(tab -> tab.getName()).collect(
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
                                                               final JDBCType cursorFieldType,
                                                               final String cursor) {
    LOGGER.info("Queueing query for table: {}", tableName);
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.query(
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

    final JdbcDatabase database = Databases.createStreamingJdbcDatabase(
        jdbcConfig.get("username").asText(),
        jdbcConfig.has("password") ? jdbcConfig.get("password").asText() : null,
        jdbcConfig.get("jdbc_url").asText(),
        driverClass,
        jdbcStreamingQueryConfiguration,
        jdbcConfig.has("connection_properties") ? jdbcConfig.get("connection_properties").asText() : null,
        getSourceOperations());

    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);

    return database;
  }

  protected JdbcSourceOperations getSourceOperations() {
    return JdbcUtils.getDefaultSourceOperations();
  }

}
