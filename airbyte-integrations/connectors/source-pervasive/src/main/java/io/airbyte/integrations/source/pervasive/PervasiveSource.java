/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.pervasive;

import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_SIZE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_COLUMN_TYPE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_DECIMAL_DIGITS;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_IS_NULLABLE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_SCHEMA_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.INTERNAL_TABLE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_COLUMN_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_DATABASE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_DATA_TYPE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_SCHEMA_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_SIZE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_TABLE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_COLUMN_TYPE_NAME;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_DECIMAL_DIGITS;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.JDBC_IS_NULLABLE;
import static io.airbyte.cdk.db.jdbc.JdbcConstants.KEY_SEQ;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.JdbcConnector;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import java.sql.JDBCType;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import java.util.List;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.db.jdbc.streaming.NoOpStreamingQueryConfig;
import io.airbyte.cdk.db.SqlDatabase;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedSource;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.cdk.integrations.source.jdbc.JdbcDataSourceUtils;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaType;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.UncheckedIOException;
import java.nio.charset.StandardCharsets;
import java.sql.JDBCType;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import javax.sql.DataSource;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.DriverManager;
import java.sql.Connection;

import io.airbyte.cdk.integrations.base.ssh.SshWrappedSource;

public class PervasiveSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PervasiveSource.class);

  // TODO insert your driver name. Ex:
  // "com.microsoft.sqlserver.jdbc.SQLServerDriver"
  static final String DRIVER_CLASS = DatabaseDriver.PERVASIVE.getDriverClassName();

  public static Source sshWrappedSource(PervasiveSource source) {
    return new SshWrappedSource(source, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public PervasiveSource() {
    // TODO: if the JDBC driver does not support custom fetch size, use
    // NoOpStreamingQueryConfig
    // instead of AdaptiveStreamingQueryConfig.
    super(DRIVER_CLASS, PervasiveAdaptiveStreamingQueryConfig::new, new PervasiveSourceOperations());
  }

  // TODO The config is based on spec.json, update according to your DB
  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final String schema = config.get(JdbcUtils.DATABASE_KEY).asText();
    final String host = config.get(JdbcUtils.HOST_KEY).asText();
    final Integer port = config.get(JdbcUtils.PORT_KEY).asInt();
    final String database = config.get(JdbcUtils.DATABASE_KEY).asText();
    final String jdbcUrl = String.format(DatabaseDriver.PERVASIVE.getUrlFormatString(), host, port, database);

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl);

    try {
      // call methods that might throw SQLException
      Class.forName("com.pervasive.jdbc.v2.Driver");
      Connection conn = DriverManager.getConnection(jdbcUrl, "", "");

    } catch (ClassNotFoundException e) {
      // do something appropriate with the exception, *at least*:
      e.printStackTrace();
    } catch (SQLException e) {
      // do something appropriate with the exception, *at least*:
      e.printStackTrace();
    }
    if (config.has("encryption_key")) {
      configBuilder.put("encryption_key",
          config.get("encryption_key").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    // TODO Add tables to exclude, Ex "INFORMATION_SCHEMA", "sys",
    // "spt_fallback_db", etc
    return Set.of(
        "X$Attrib",
        "X$Field",
        "X$File",
        "X$Index",
        "X$Occurs",
        "X$Proc",
        "X$Relate",
        "X$Trigger",
        "X$Variant",
        "X$View"
        );
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(JdbcDatabase database) throws Exception {
    return discoverInternal(database,
        database.getSourceConfig().has(JdbcUtils.DATABASE_KEY)
            ? database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText()
            : null);
  }

  private List<String> extractCursorFields(final List<JsonNode> fields) {
    return fields.stream()
        .filter(field -> isCursorType(sourceOperations.getDatabaseFieldType(field)))
        .map(field -> field.get(INTERNAL_COLUMN_NAME).asText())
        .collect(Collectors.toList());
  }

  @Override
  public JdbcDatabase createDatabase(JsonNode sourceConfig, String delimiter) throws SQLException {
    final JsonNode jdbcConfig = toDatabaseConfig(sourceConfig);
    Map<String, String> connectionProperties = JdbcDataSourceUtils.getConnectionProperties(sourceConfig, delimiter);
    // Create the data source
    final DataSource dataSource = DataSourceFactory.create(
        jdbcConfig.has(JdbcUtils.USERNAME_KEY) ? jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText() : null,
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        driverClassName,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        connectionProperties,
        getConnectionTimeout(connectionProperties),
        "select 1;");

    // Record the data source so that it can be closed.
    dataSources.add(dataSource);

    final JdbcDatabase database = new StreamingJdbcDatabase(
        dataSource,
        sourceOperations,
        streamingQueryConfigProvider);

    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(jdbcConfig);

    if (jdbcConfig.has("encryption_key")) {
      database.execute("set owner='" + jdbcConfig.get("encryption_key").asText() + "';");
    }
    return database;
  }

  // We need to do this because .getMetaData().getColumns is too slow !
  // connection -> connection.getMetaData().getColumns(getCatalog(database), schema, null, null),
  @Override
  protected List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database, final String schema)
      throws Exception {
    final Set<String> internalSchemas = new HashSet<>(getExcludedInternalNameSpaces());
    LOGGER.info("Internal schemas to exclude: {}", internalSchemas);
    final Set<JdbcPrivilegeDto> tablesWithSelectGrantPrivilege = getPrivilegesTableForCurrentUser(database, schema);
    List<JsonNode> columnsInfo;

    String query = "select '" + schema
        + "' as \"TABLE_SCHEM\", 	file.xf$name as \"TABLE_NAME\",  	field.xe$name as \"COLUMN_NAME\",  	field.xe$DataType as \"TYPE_NAME\", field.xe$DataType as \"DATA_TYPE\",	field.xe$Dec as \"DECIMAL_DIGITS\", 	field.xe$Flags as \"IS_NULLABLE\", 	field.xe$Size as \"COLUMN_SIZE\" from x$field field  join x$file file on xe$file = xf$id WHERE  field.xe$DataType != 255 	and field.xe$DataType != 227;";

    LOGGER.info("Get columns: {}", query);
    columnsInfo = database.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery(query),
        this::getColumnMetadata);

    return columnsInfo.stream()
        .filter(excludeNotAccessibleTables(internalSchemas, tablesWithSelectGrantPrivilege))
        // group by schema and table name to handle the case where a table with the same
        // name exists in
        // multiple schemas.
        .collect(Collectors.groupingBy(
            t -> ImmutablePair.of(t.get(INTERNAL_SCHEMA_NAME).asText(), t.get(INTERNAL_TABLE_NAME).asText())))
        .values()
        .stream()
        .map(fields -> TableInfo.<CommonField<JDBCType>>builder()
            .nameSpace(fields.get(0).get(INTERNAL_SCHEMA_NAME).asText())
            .name(fields.get(0).get(INTERNAL_TABLE_NAME).asText())
            .fields(fields.stream()
                // read the column metadata Json object, and determine its type
                .map(f -> {
                  final JDBCType datatype = sourceOperations.getDatabaseFieldType(f);

                  final JsonSchemaType jsonType = getAirbyteType(datatype);
                  LOGGER.debug("Table {} column {} (type {}[{}], nullable {}) -> {}",
                      fields.get(0).get(INTERNAL_TABLE_NAME).asText().trim(),
                      f.get(INTERNAL_COLUMN_NAME).asText().trim(),
                      f.get(INTERNAL_COLUMN_TYPE_NAME).asText().trim(),
                      f.get(INTERNAL_COLUMN_SIZE).asInt(),
                      f.get(INTERNAL_IS_NULLABLE).asInt() == 2,
                      jsonType);

                  return new CommonField<JDBCType>(f.get(INTERNAL_COLUMN_NAME).asText(), datatype) {
                  };
                })
                .collect(Collectors.toList()))
            .cursorFields(extractCursorFields(fields))
            .build())
        .collect(Collectors.toList());
  }

  private JsonNode getColumnMetadata(final ResultSet resultSet) throws SQLException {
    final var fieldMap = ImmutableMap.<String, Object>builder()
        // we always want a namespace, if we cannot get a schema, use db name.
        .put(INTERNAL_SCHEMA_NAME,
            resultSet.getObject(JDBC_COLUMN_SCHEMA_NAME) != null ? resultSet.getString(JDBC_COLUMN_SCHEMA_NAME)
                : resultSet.getObject(JDBC_COLUMN_DATABASE_NAME))
        .put(INTERNAL_TABLE_NAME, resultSet.getString(JDBC_COLUMN_TABLE_NAME).trim())
        .put(INTERNAL_COLUMN_NAME, resultSet.getString(JDBC_COLUMN_COLUMN_NAME).trim())
        .put(INTERNAL_COLUMN_TYPE, resultSet.getInt(JDBC_COLUMN_DATA_TYPE))
        .put(INTERNAL_COLUMN_TYPE_NAME, resultSet.getInt(JDBC_COLUMN_TYPE_NAME))
        .put(INTERNAL_COLUMN_SIZE, resultSet.getInt(JDBC_COLUMN_SIZE))
        .put(INTERNAL_IS_NULLABLE, resultSet.getInt(JDBC_IS_NULLABLE) == 2);
    if (resultSet.getString(JDBC_DECIMAL_DIGITS) != null) {
      fieldMap.put(INTERNAL_DECIMAL_DIGITS, resultSet.getString(JDBC_DECIMAL_DIGITS));
    }
    return Jsons.jsonNode(fieldMap.build());
  }

  private String getCatalog(final SqlDatabase database) {
    var return_data = (database.getSourceConfig().has(JdbcUtils.DATABASE_KEY)
        ? database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText()
        : null);
    return return_data;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = PervasiveSource.sshWrappedSource(new PervasiveSource());
    LOGGER.info("starting source: {}", PervasiveSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PervasiveSource.class);
  }
}
