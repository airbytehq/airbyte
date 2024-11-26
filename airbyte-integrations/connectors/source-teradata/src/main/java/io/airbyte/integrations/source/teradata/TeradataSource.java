/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata;

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
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.cdk.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.cdk.db.SqlDatabase;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedSource;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.cdk.integrations.source.jdbc.JdbcDataSourceUtils;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.CursorInfo;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.stream.Stream;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifier;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.enquoteIdentifierList;
import static io.airbyte.cdk.integrations.source.relationaldb.RelationalDbQueryUtils.queryTable;
import java.sql.PreparedStatement;
import io.airbyte.commons.stream.AirbyteStreamUtils;
import java.util.Optional;
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
import java.util.Arrays;
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

public class TeradataSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(TeradataSource.class);

  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  public static final String DRIVER_CLASS = DatabaseDriver.TERADATA.getDriverClassName();

  public static final String PARAM_DBS_PORT = "dbs_port";
  public static final String PARAM_MODE = "mode";
  public static final String PARAM_SSL = "ssl";
  public static final String PARAM_SSL_MODE = "ssl_mode";
  public static final String PARAM_SSLMODE = "sslmode";
  public static final String PARAM_SSLCA = "sslca";
  public static final String REQUIRE = "require";

  private static final String CA_CERTIFICATE = "ca.pem";

  public static Source sshWrappedSource(TeradataSource source) {
    return new SshWrappedSource(source, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public TeradataSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new TeradataSourceOperations());
  }

  public static void main(final String[] args) throws Exception {
    final Source source = TeradataSource.sshWrappedSource(new TeradataSource());
    LOGGER.info("starting source: {}", TeradataSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", TeradataSource.class);
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final String schema = config.get(JdbcUtils.DATABASE_KEY).asText();
    final String host = config.get(JdbcUtils.HOST_KEY).asText();
    final String jdbcUrl = String.format(DatabaseDriver.TERADATA.getUrlFormatString(), host);

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl)
        .put(JdbcUtils.SCHEMA_KEY, schema);

    if (config.has(JdbcUtils.PORT_KEY)) {
      configBuilder.put(JdbcUtils.PORT_KEY, config.get(JdbcUtils.PORT_KEY).asText());
    }

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    if (config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)) {
      configBuilder.put(JdbcUtils.JDBC_URL_PARAMS_KEY, config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }

    if (config.has("unwanted_tables")) {
      configBuilder.put("unwanted_tables", config.get("unwanted_tables").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    // the connector requires to have a database explicitly defined
    return Set.of("");
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(JdbcDatabase database) throws Exception {
    return discoverInternal(database, database.getSourceConfig().has(JdbcUtils.DATABASE_KEY) ? database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText() : null);
  }


  @Override
  protected List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database, final String schema) throws Exception {
    final Set<String> internalSchemas = new HashSet<>(getExcludedInternalNameSpaces());
    LOGGER.info("Internal schemas to exclude: {}", internalSchemas);
    final Set<JdbcPrivilegeDto> tablesWithSelectGrantPrivilege = getPrivilegesTableForCurrentUser(database, schema);
    List<JsonNode> columnsInfo;
    var catalog = getCatalog(database);
    
    try {
      columnsInfo = database.bufferedResultSetQuery(
        connection -> connection.getMetaData().getColumns(catalog, catalog.toUpperCase(), null, null),
        this::getColumnMetadata);
    } catch (final Exception getColumnsError) {
      LOGGER.info("EXCEPTION: unable to run getColumns on all tables in schema: '{}'", schema);
      var query = "SELECT DataBaseName, TableName FROM DBC.TablesV WHERE DatabaseName = '" + catalog.toUpperCase() + "' ORDER BY TableName;";
      columnsInfo = new ArrayList<JsonNode>();
      LOGGER.info("Getting all tables with: '{}'", query);
      var tableRows = database.bufferedResultSetQuery(
        conn -> conn.createStatement().executeQuery(query),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
      for (final JsonNode tableRow : tableRows) {
        var DataBaseName = tableRow.get("DataBaseName").asText();
        String TableName = tableRow.get("TableName").asText();
        LOGGER.info("Looking in table: '{}'", TableName);
        if (database.getDatabaseConfig().has("unwanted_tables")) {
          if (Arrays.stream(database.getDatabaseConfig().get("unwanted_tables").asText().split(",")).anyMatch(tableRow.get("TableName").asText()::equals)){
            continue;
          }
        }
        try {
          columnsInfo.addAll(database.bufferedResultSetQuery(
            connection -> connection.getMetaData().getColumns(catalog, DataBaseName, TableName, null),
            this::getColumnMetadata));
        } catch (final Exception e) {
          LOGGER.info("FAILING ON schema: '{}' and table: '{}'", DataBaseName, TableName);
        }
      }
    }

    // return columnsInfo.stream()
    //     .filter(excludeNotAccessibleTables(internalSchemas, tablesWithSelectGrantPrivilege))
    //     // group by schema and table name to handle the case where a table with the same name exists in
    //     // multiple schemas.
    //     .collect(Collectors.groupingBy(t -> ImmutablePair.of(t.get(INTERNAL_SCHEMA_NAME).asText(), t.get(INTERNAL_TABLE_NAME).asText())))
    //     .values()
    //     .stream()
    //     .map(fields -> TableInfo.<CommonField<JDBCType>>builder()
    //         .nameSpace(fields.get(0).get(INTERNAL_SCHEMA_NAME).asText())
    //         .name(fields.get(0).get(INTERNAL_TABLE_NAME).asText())
    //         .fields(fields.stream()
    //             // read the column metadata Json object, and determine its type
    //             .map(f -> {
    //               final JDBCType datatype = sourceOperations.getDatabaseFieldType(f);
    //               final JsonSchemaType jsonType = getAirbyteType(datatype);
    //               LOGGER.debug("Table {} column {} (type {}[{}], nullable {}) -> {}",
    //                   fields.get(0).get(INTERNAL_TABLE_NAME).asText(),
    //                   f.get(INTERNAL_COLUMN_NAME).asText(),
    //                   f.get(INTERNAL_COLUMN_TYPE_NAME).asText(),
    //                   f.get(INTERNAL_COLUMN_SIZE).asInt(),
    //                   f.get(INTERNAL_IS_NULLABLE).asBoolean(),
    //                   jsonType);
    //               return new CommonField<JDBCType>(f.get(INTERNAL_COLUMN_NAME).asText(), datatype) {};
    //             })
    //             .collect(Collectors.toList()))
    //         .cursorFields(extractCursorFields(fields))
    //         .build())
    //     .collect(Collectors.toList());

    return columnsInfo.stream()
      .filter(excludeNotAccessibleTables(internalSchemas, tablesWithSelectGrantPrivilege))
      .collect(Collectors.groupingBy(t -> ImmutablePair.of(t.get(INTERNAL_SCHEMA_NAME).asText(), t.get(INTERNAL_TABLE_NAME).asText())))
      .values()
      .stream()
      .flatMap(fields -> {
        String schemaName = fields.get(0).get(INTERNAL_SCHEMA_NAME).asText();
        String tableName = fields.get(0).get(INTERNAL_TABLE_NAME).asText();
        String duplicatedTableName = tableName + "_COPY"; // or prefix/suffix of your choice

        List<CommonField<JDBCType>> commonFields = fields.stream()
            .map(f -> {
              final JDBCType datatype = sourceOperations.getDatabaseFieldType(f);
              final JsonSchemaType jsonType = getAirbyteType(datatype);
              LOGGER.debug("Table {} column {} (type {}[{}], nullable {}) -> {}",
                  tableName,
                  f.get(INTERNAL_COLUMN_NAME).asText(),
                  f.get(INTERNAL_COLUMN_TYPE_NAME).asText(),
                  f.get(INTERNAL_COLUMN_SIZE).asInt(),
                  f.get(INTERNAL_IS_NULLABLE).asBoolean(),
                  jsonType);
              return new CommonField<JDBCType>(f.get(INTERNAL_COLUMN_NAME).asText(), datatype) {};
            })
            .collect(Collectors.toList());

        TableInfo<CommonField<JDBCType>> original = TableInfo.<CommonField<JDBCType>>builder()
            .nameSpace(schemaName)
            .name(tableName)
            .fields(commonFields)
            .cursorFields(extractCursorFields(fields))
            .build();

        
        boolean hasActiveFlag = fields.stream()
          .anyMatch(f -> f.get(INTERNAL_COLUMN_NAME).asText().equalsIgnoreCase("active_flag"));

          if (hasActiveFlag) {
            TableInfo<CommonField<JDBCType>> active = TableInfo.<CommonField<JDBCType>>builder()
            .nameSpace(schemaName)
            .name(tableName + "_active")
            .fields(commonFields)
            .cursorFields(extractCursorFields(fields))
            .build();
        
          TableInfo<CommonField<JDBCType>> inactive = TableInfo.<CommonField<JDBCType>>builder()
            .nameSpace(schemaName)
            .name(tableName + "_inactive")
            .fields(commonFields)
            .cursorFields(extractCursorFields(fields))
            .build();

            return Stream.of(original, active, inactive);
          } else {
            return Stream.of(original);
          }
      })
      .collect(Collectors.toList());
  }

  private JsonNode getColumnMetadata(final ResultSet resultSet) throws SQLException {
    LOGGER.info("Looking in table to get columns: '{}'", resultSet.getString(JDBC_COLUMN_TABLE_NAME));

    final var fieldMap = ImmutableMap.<String, Object>builder()
        // we always want a namespace, if we cannot get a schema, use db name.
        .put(INTERNAL_SCHEMA_NAME,
            resultSet.getObject(JDBC_COLUMN_SCHEMA_NAME) != null ? resultSet.getString(JDBC_COLUMN_SCHEMA_NAME)
                : resultSet.getObject(JDBC_COLUMN_DATABASE_NAME))
        .put(INTERNAL_TABLE_NAME, resultSet.getString(JDBC_COLUMN_TABLE_NAME))
        .put(INTERNAL_COLUMN_NAME, resultSet.getString(JDBC_COLUMN_COLUMN_NAME))
        .put(INTERNAL_COLUMN_TYPE, resultSet.getString(JDBC_COLUMN_DATA_TYPE))
        .put(INTERNAL_COLUMN_TYPE_NAME, resultSet.getString(JDBC_COLUMN_TYPE_NAME))
        .put(INTERNAL_COLUMN_SIZE, resultSet.getInt(JDBC_COLUMN_SIZE))
        .put(INTERNAL_IS_NULLABLE, resultSet.getString(JDBC_IS_NULLABLE));
    if (resultSet.getString(JDBC_DECIMAL_DIGITS) != null) {
      fieldMap.put(INTERNAL_DECIMAL_DIGITS, resultSet.getString(JDBC_DECIMAL_DIGITS));
    }
    return Jsons.jsonNode(fieldMap.build());
  }
  private String getCatalog(final SqlDatabase database) {
    var return_data = (database.getSourceConfig().has(JdbcUtils.DATABASE_KEY) ? database.getSourceConfig().get(JdbcUtils.DATABASE_KEY).asText() : null);
    return return_data;
  }

  private List<String> extractCursorFields(final List<JsonNode> fields) {
    return fields.stream()
        .filter(field -> isCursorType(sourceOperations.getDatabaseFieldType(field)))
        .map(field -> field.get(INTERNAL_COLUMN_NAME).asText())
        .collect(Collectors.toList());
  }

  @Override
  public JdbcDatabase createDatabase(JsonNode sourceConfig) throws SQLException {
    final Map<String, String> customProperties = JdbcUtils.parseJdbcParameters(sourceConfig, JdbcUtils.JDBC_URL_PARAMS_KEY);
    final Map<String, String> sslConnectionProperties = getSslConnectionProperties(sourceConfig);
    final Map<String, String> portProperty = getPortProperty(sourceConfig);
    JdbcDataSourceUtils.assertCustomParametersDontOverwriteDefaultParameters(customProperties, sslConnectionProperties);

    final JsonNode jdbcConfig = toDatabaseConfig(sourceConfig);
    final Map<String, String> connectionProperties = MoreMaps.merge(customProperties, sslConnectionProperties, portProperty);

    // Create the data source
    final DataSource dataSource = DataSourceFactory.create(
        jdbcConfig.has(JdbcUtils.USERNAME_KEY) ? jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText() : null,
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        driverClassName,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        connectionProperties,
        getConnectionTimeout(connectionProperties, driverClassName));
    // Record the data source so that it can be closed.
    dataSources.add(dataSource);

    final JdbcDatabase database = new StreamingJdbcDatabase(
        dataSource,
        sourceOperations,
        streamingQueryConfigProvider);

    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(jdbcConfig);
    return database;
  }

  private Map<String, String> getPortProperty(JsonNode config) {
    final Map<String, String> additionalParameters = new HashMap<>();

    if (config.has(JdbcUtils.PORT_KEY)) {
      LOGGER.debug("Using custom port");
      additionalParameters.put(TeradataSource.PARAM_DBS_PORT, config.get(JdbcUtils.PORT_KEY).asText());
    }

    return additionalParameters;
  }

  private Map<String, String> getSslConnectionProperties(JsonNode config) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (config.has(PARAM_SSL) && config.get(PARAM_SSL).asBoolean()) {
      LOGGER.debug("SSL Enabled");
      if (config.has(PARAM_SSL_MODE)) {
        LOGGER.debug("Selected SSL Mode : {}", config.get(PARAM_SSL_MODE).get(PARAM_MODE).asText());
        additionalParameters.putAll(obtainConnectionOptions(config.get(PARAM_SSL_MODE)));
      } else {
        additionalParameters.put(PARAM_SSLMODE, REQUIRE);
      }
    }
    return additionalParameters;
  }

  private Map<String, String> obtainConnectionOptions(final JsonNode encryption) {
    final Map<String, String> additionalParameters = new HashMap<>();
    if (!encryption.isNull()) {
      final var method = encryption.get(PARAM_MODE).asText();
      switch (method) {
        case "verify-ca", "verify-full" -> {
          additionalParameters.put(PARAM_SSLMODE, method);
          try {
            createCertificateFile(CA_CERTIFICATE, encryption.get("ssl_ca_certificate").asText());
          } catch (final IOException ioe) {
            throw new UncheckedIOException(ioe);
          }
          additionalParameters.put(PARAM_SSLCA, CA_CERTIFICATE);
        }
        default -> additionalParameters.put(PARAM_SSLMODE, method);
      }
    }
    return additionalParameters;
  }

  private static void createCertificateFile(String fileName, String fileValue) throws IOException {
    try (final PrintWriter out = new PrintWriter(fileName, StandardCharsets.UTF_8)) {
      out.print(fileValue);
    }
  }


  @Override
  protected AutoCloseableIterator<JsonNode> queryTableFullRefresh(final JdbcDatabase database,
                                                                  final List<String> columnNames,
                                                                  final String schemaName,
                                                                  final String tableName,
                                                                  final SyncMode syncMode,
                                                                  final Optional<String> cursorField) {
    LOGGER.info("CUSTOM Queueing queryTableFullRefresh query for table: {}", tableName);
    if (tableName.endsWith("_inactive")  || tableName.endsWith("_active")) {
      var stripTableName = tableName.endsWith("_inactive") ? tableName.substring(0, tableName.length() - 9): tableName.substring(0, tableName.length() - 7);
      LOGGER.info("CUSTOM Queueing queryTableFullRefresh active/inactive: {}", stripTableName);
      if (syncMode.equals(SyncMode.INCREMENTAL) && getStateEmissionFrequency() > 0) {
      final String quotedCursorField = enquoteIdentifier(cursorField.get(), getQuoteString());
      return queryTable(database, String.format("SELECT %s FROM %s WHERE active_flag='%s' ORDER BY %s ASC",
          enquoteIdentifierList(columnNames, getQuoteString()),
          getFullyQualifiedTableNameWithQuoting(schemaName, stripTableName, getQuoteString()), tableName.endsWith("_active") ? "Y": "N", quotedCursorField),
          tableName, schemaName);
    } else {
      return queryTable(database, String.format("SELECT %s FROM %s WHERE active_flag='%s' ",
          enquoteIdentifierList(columnNames, getQuoteString()),
          getFullyQualifiedTableNameWithQuoting(schemaName, stripTableName, getQuoteString()), tableName.endsWith("_active") ? "Y": "N"), tableName, schemaName);
    }

    } else {
      return super.queryTableFullRefresh(database,columnNames,schemaName,tableName,syncMode,cursorField);
    }
  }

  @Override
  public AutoCloseableIterator<JsonNode> queryTableIncremental(final JdbcDatabase database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName,
                                                               final CursorInfo cursorInfo,
                                                               final JDBCType cursorFieldType) {
    LOGGER.info("CUSTOM Queueing queryTableIncremental query for table: {}", tableName);

    if (tableName.endsWith("_inactive")  || tableName.endsWith("_active")) {
      var stripTableName = tableName.endsWith("_inactive") ? tableName.substring(0, tableName.length() - 9): tableName.substring(0, tableName.length() - 7);

      final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair airbyteStream =
          AirbyteStreamUtils.convertFromNameAndNamespace(tableName, schemaName);
      return AutoCloseableIterators.lazyIterator(() -> {
        try {
          final Stream<JsonNode> stream = database.unsafeQuery(
              connection -> {
                LOGGER.info("Preparing query for table: {}", stripTableName);
                final String fullTableName = getFullyQualifiedTableNameWithQuoting(schemaName, stripTableName, getQuoteString());
                final String quotedCursorField = enquoteIdentifier(cursorInfo.getCursorField(), getQuoteString());
  
                final String operator;
                if (cursorInfo.getCursorRecordCount() <= 0L) {
                  operator = ">";
                } else {
                  final long actualRecordCount = getActualCursorRecordCount(
                      connection, fullTableName, quotedCursorField, cursorFieldType, cursorInfo.getCursor());
                  LOGGER.info("Table {} cursor count: expected {}, actual {}", stripTableName, cursorInfo.getCursorRecordCount(), actualRecordCount);
                  if (actualRecordCount == cursorInfo.getCursorRecordCount()) {
                    operator = ">";
                  } else {
                    operator = ">=";
                  }
                }
  
                final String wrappedColumnNames = getWrappedColumnNames(database, connection, columnNames, schemaName, stripTableName);
                final StringBuilder sql = new StringBuilder(String.format("SELECT %s FROM %s WHERE active_flag='%s' and %s %s ?",
                    wrappedColumnNames,
                    fullTableName,
                    tableName.endsWith("_active") ? "Y": "N",
                    quotedCursorField,
                    operator));
                // if the connector emits intermediate states, the incremental query must be sorted by the cursor
                // field
                if (getStateEmissionFrequency() > 0) {
                  sql.append(String.format(" ORDER BY %s ASC", quotedCursorField));
                }
  
                final PreparedStatement preparedStatement = connection.prepareStatement(sql.toString());
                LOGGER.info("Executing query for table {}: {}", stripTableName, preparedStatement);
                sourceOperations.setCursorField(preparedStatement, 1, cursorFieldType, cursorInfo.getCursor());
                return preparedStatement;
              },
              sourceOperations::rowToJson);
          return AutoCloseableIterators.fromStream(stream, airbyteStream);
        } catch (final SQLException e) {
          throw new RuntimeException(e);
        }
      }, airbyteStream);
    } else {
      return super.queryTableIncremental(database,columnNames,schemaName,tableName,cursorInfo,cursorFieldType);
    }

  }

}
