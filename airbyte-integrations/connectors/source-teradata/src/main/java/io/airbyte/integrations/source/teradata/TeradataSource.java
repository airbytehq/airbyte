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
    
    try {
      columnsInfo = database.bufferedResultSetQuery(
        connection -> connection.getMetaData().getColumns(getCatalog(database), schema, null, null),
        this::getColumnMetadata);
    } catch (final Exception getColumnsError) {
      LOGGER.info("EXCEPTION: unable to run getColumns on all tables in schema: '{}'", schema);
      var query = "SELECT DataBaseName, TableName FROM DBC.TablesV WHERE DatabaseName = '" + getCatalog(database).toUpperCase() + "' ORDER BY TableName;";
      columnsInfo = new ArrayList<JsonNode>();
      var tableRows = database.bufferedResultSetQuery(
        conn -> conn.createStatement().executeQuery(query),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
      for (final JsonNode tableRow : tableRows) {
        var DataBaseName = tableRow.get("DataBaseName").asText();
        var TableName = tableRow.get("TableName").asText();
        try {
          columnsInfo.addAll(database.bufferedResultSetQuery(
            connection -> connection.getMetaData().getColumns(getCatalog(database), DataBaseName, TableName, null),
            this::getColumnMetadata));
        } catch (final Exception e) {
          LOGGER.info("FAILING ON schema: '{}' and table: '{}'", DataBaseName, TableName);
        }
      }
    }

    return columnsInfo.stream()
        .filter(excludeNotAccessibleTables(internalSchemas, tablesWithSelectGrantPrivilege))
        // group by schema and table name to handle the case where a table with the same name exists in
        // multiple schemas.
        .collect(Collectors.groupingBy(t -> ImmutablePair.of(t.get(INTERNAL_SCHEMA_NAME).asText(), t.get(INTERNAL_TABLE_NAME).asText())))
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
                      fields.get(0).get(INTERNAL_TABLE_NAME).asText(),
                      f.get(INTERNAL_COLUMN_NAME).asText(),
                      f.get(INTERNAL_COLUMN_TYPE_NAME).asText(),
                      f.get(INTERNAL_COLUMN_SIZE).asInt(),
                      f.get(INTERNAL_IS_NULLABLE).asBoolean(),
                      jsonType);
                  return new CommonField<JDBCType>(f.get(INTERNAL_COLUMN_NAME).asText(), datatype) {};
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

}
