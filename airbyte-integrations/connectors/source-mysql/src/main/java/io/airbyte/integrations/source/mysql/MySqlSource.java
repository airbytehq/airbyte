/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.db.jdbc.JdbcUtils.EQUALS;
import static io.airbyte.integrations.debezium.AirbyteDebeziumHandler.shouldUseCDC;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils.SSL_MODE;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.debezium.internals.FirstRecordWaitTimeUtil;
import io.airbyte.integrations.debezium.internals.mysql.MySqlCdcPosition;
import io.airbyte.integrations.debezium.internals.mysql.MySqlCdcTargetPosition;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils;
import io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils.SslMode;
import io.airbyte.integrations.source.mysql.helpers.CdcConfigurationHelper;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlSource extends AbstractJdbcSource<MysqlType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlSource.class);
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;
  public static final String NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY =
      """
        SELECT (EXISTS (SELECT * from `%s`.`%s` where `%s` IS NULL LIMIT 1)) AS %s
      """;
  public static final String NULL_CURSOR_VALUE_WITHOUT_SCHEMA_QUERY =
      """
      SELECT (EXISTS (SELECT * from %s where `%s` IS NULL LIMIT 1)) AS %s
      """;
  public static final String DESCRIBE_TABLE_WITHOUT_SCHEMA_QUERY =
      """
      DESCRIBE %s
      """;
  public static final String DESCRIBE_TABLE_WITH_SCHEMA_QUERY =
      """
      DESCRIBE `%s`.`%s`
      """;

  public static final String DRIVER_CLASS = DatabaseDriver.MYSQL.getDriverClassName();
  public static final String MYSQL_CDC_OFFSET = "mysql_cdc_offset";
  public static final String MYSQL_DB_HISTORY = "mysql_db_history";
  public static final String CDC_LOG_FILE = "_ab_cdc_log_file";
  public static final String CDC_LOG_POS = "_ab_cdc_log_pos";
  public static final List<String> SSL_PARAMETERS = List.of(
      "useSSL=true",
      "requireSSL=true");

  private final FeatureFlags featureFlags;

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new MySqlSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  public MySqlSource() {
    super(DRIVER_CLASS, MySqlStreamingQueryConfig::new, new MySqlSourceOperations());
    this.featureFlags = new EnvVariableFeatureFlags();
  }

  private static AirbyteStream overrideSyncModes(final AirbyteStream stream) {
    return stream.withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
  }

  private static AirbyteStream removeIncrementalWithoutPk(final AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      stream.getSupportedSyncModes().remove(SyncMode.INCREMENTAL);
    }

    return stream;
  }

  private static AirbyteStream setIncrementalToSourceDefined(final AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setSourceDefinedCursor(true);
    }

    return stream;
  }

  // Note: in place mutation.
  private static AirbyteStream addCdcMetadataColumns(final AirbyteStream stream) {

    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LOG_FILE, stringType);
    properties.set(CDC_LOG_POS, numberType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);

    return stream;
  }

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config) throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(super.getCheckOperations(config));
    if (isCdc(config)) {
      checkOperations.addAll(CdcConfigurationHelper.getCheckOperations());

      checkOperations.add(database -> {
        FirstRecordWaitTimeUtil.checkFirstRecordWaitTime(config);
        CdcConfigurationHelper.checkServerTimeZoneConfig(config);
      });
    }
    return checkOperations;
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    final AirbyteCatalog catalog = super.discover(config);

    if (isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(MySqlSource::overrideSyncModes)
          .map(MySqlSource::removeIncrementalWithoutPk)
          .map(MySqlSource::setIncrementalToSourceDefined)
          .map(MySqlSource::addCdcMetadataColumns)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final String encodedDatabaseName = HostPortResolver.encodeValue(config.get(JdbcUtils.DATABASE_KEY).asText());
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        encodedDatabaseName));

    // To fetch the result in batches, the "useCursorFetch=true" must be set.
    // https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-implementation-notes.html.
    // When using this approach MySql creates a temporary table which may have some effect on db
    // performance.
    jdbcUrl.append("?useCursorFetch=true");
    jdbcUrl.append("&zeroDateTimeBehavior=convertToNull");
    // ensure the return tinyint(1) is boolean
    jdbcUrl.append("&tinyInt1isBit=true");
    // ensure the return year value is a Date; see the rationale
    // in the setJsonField method in MySqlSourceOperations.java
    jdbcUrl.append("&yearIsDateType=true");
    if (config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      jdbcUrl.append(JdbcUtils.AMPERSAND).append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText());
    }
    final Map<String, String> sslParameters = JdbcSSLConnectionUtils.parseSSLConfig(config);
    jdbcUrl.append(JdbcUtils.AMPERSAND).append(toJDBCQueryParams(sslParameters));

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    configBuilder.putAll(sslParameters);

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }
    return Jsons.jsonNode(configBuilder.build());
  }

  /**
   * Generates SSL related query parameters from map of parsed values.
   *
   * @apiNote Different connector may need an override for specific implementation
   * @param sslParams
   * @return SSL portion of JDBC question params or and empty string
   */
  private String toJDBCQueryParams(final Map<String, String> sslParams) {
    return Objects.isNull(sslParams) ? ""
        : sslParams.entrySet()
            .stream()
            .map((entry) -> {
              if (entry.getKey().equals(SSL_MODE)) {
                return entry.getKey() + EQUALS + toSslJdbcParam(SslMode.valueOf(entry.getValue()));
              } else {
                return entry.getKey() + EQUALS + entry.getValue();
              }
            })
            .collect(Collectors.joining(JdbcUtils.AMPERSAND));
  }

  private static boolean isCdc(final JsonNode config) {
    if (config.hasNonNull("replication_method")) {
      if (config.get("replication_method").isTextual()) {
        return ReplicationMethod.valueOf(config.get("replication_method").asText())
            .equals(ReplicationMethod.CDC);
      } else if (config.get("replication_method").isObject()) {
        return config.get("replication_method").get("method").asText()
            .equals(ReplicationMethod.CDC.name());
      }
    }
    return false;
  }

  @Override
  protected AirbyteStateType getSupportedStateType(final JsonNode config) {
    if (!featureFlags.useStreamCapableState()) {
      return AirbyteStateType.LEGACY;
    }

    return isCdc(config) ? AirbyteStateType.GLOBAL : AirbyteStateType.STREAM;
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (isCdc(sourceConfig) && shouldUseCDC(catalog)) {
      final Duration firstRecordWaitTime = FirstRecordWaitTimeUtil.getFirstRecordWaitTime(sourceConfig);
      LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());
      final AirbyteDebeziumHandler<MySqlCdcPosition> handler =
          new AirbyteDebeziumHandler<>(sourceConfig, MySqlCdcTargetPosition.targetPosition(database), true, firstRecordWaitTime);

      final MySqlCdcStateHandler mySqlCdcStateHandler = new MySqlCdcStateHandler(stateManager);
      final MySqlCdcConnectorMetadataInjector mySqlCdcConnectorMetadataInjector = new MySqlCdcConnectorMetadataInjector();

      final List<ConfiguredAirbyteStream> streamsToSnapshot = identifyStreamsToSnapshot(catalog, stateManager);
      final Optional<CdcState> cdcState = Optional.ofNullable(stateManager.getCdcStateManager().getCdcState());

      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(catalog,
          new MySqlCdcSavedInfoFetcher(cdcState.orElse(null)),
          new MySqlCdcStateHandler(stateManager),
          new MySqlCdcConnectorMetadataInjector(),
          MySqlCdcProperties.getDebeziumProperties(database),
          emittedAt,
          false);

      if (streamsToSnapshot.isEmpty()) {
        return Collections.singletonList(incrementalIteratorSupplier.get());
      }

      final AutoCloseableIterator<AirbyteMessage> snapshotIterator = handler.getSnapshotIterators(
          new ConfiguredAirbyteCatalog().withStreams(streamsToSnapshot),
          mySqlCdcConnectorMetadataInjector,
          MySqlCdcProperties.getSnapshotProperties(database),
          mySqlCdcStateHandler,
          emittedAt);

      return Collections.singletonList(
          AutoCloseableIterators.concatWithEagerClose(snapshotIterator, AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier)));
    } else {
      LOGGER.info("using CDC: {}", false);
      return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager,
          emittedAt);
    }
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "information_schema",
        "mysql",
        "performance_schema",
        "sys");
  }

  @Override
  protected boolean verifyCursorColumnValues(final JdbcDatabase database, final String schema, final String tableName, final String columnName)
      throws SQLException {
    final boolean nullValExist;
    final String resultColName = "nullValue";
    final String descQuery = schema == null || schema.isBlank()
        ? String.format(DESCRIBE_TABLE_WITHOUT_SCHEMA_QUERY, tableName)
        : String.format(DESCRIBE_TABLE_WITH_SCHEMA_QUERY, schema, tableName);
    final List<JsonNode> tableRows = database.bufferedResultSetQuery(conn -> conn.createStatement()
        .executeQuery(descQuery),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));

    Optional<JsonNode> field = Optional.empty();
    String nullableColumnName = "";
    for (final JsonNode tableRow : tableRows) {
      LOGGER.info("MySQL Table Structure {}, {}, {}", tableRow.toString(), schema, tableName);
      if (tableRow.get("Field") != null && tableRow.get("Field").asText().equalsIgnoreCase(columnName)) {
        field = Optional.of(tableRow);
        nullableColumnName = "Null";
      } else if (tableRow.get("COLUMN_NAME") != null && tableRow.get("COLUMN_NAME").asText().equalsIgnoreCase(columnName)) {
        field = Optional.of(tableRow);
        nullableColumnName = "IS_NULLABLE";
      }
    }
    if (field.isPresent()) {
      final JsonNode jsonNode = field.get();
      final JsonNode isNullable = jsonNode.get(nullableColumnName);
      if (isNullable != null) {
        if (isNullable.asText().equalsIgnoreCase("YES")) {
          final String query = schema == null || schema.isBlank()
              ? String.format(NULL_CURSOR_VALUE_WITHOUT_SCHEMA_QUERY,
                  tableName, columnName, resultColName)
              : String.format(NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY,
                  schema, tableName, columnName, resultColName);

          LOGGER.debug("null value query: {}", query);
          final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(query),
              resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
          Preconditions.checkState(jsonNodes.size() == 1);
          nullValExist = convertToBoolean(jsonNodes.get(0).get(resultColName).toString());
          LOGGER.info("null cursor value for MySQL source : {}, shema {} , tableName {}, columnName {} ", nullValExist, schema, tableName,
              columnName);
        }
      }
    }
    // return !nullValExist;
    // will enable after we have sent comms to users this affects
    return true;
  }

  private boolean convertToBoolean(final String value) {
    return "1".equalsIgnoreCase(value) || "true".equalsIgnoreCase(value);
  }

  private String toSslJdbcParam(final SslMode sslMode) {
    return toSslJdbcParamInternal(sslMode);
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  protected static String toSslJdbcParamInternal(final SslMode sslMode) {
    final var result = switch (sslMode) {
      case DISABLED, PREFERRED, REQUIRED, VERIFY_CA, VERIFY_IDENTITY -> sslMode.name();
      default -> throw new IllegalArgumentException("unexpected ssl mode");
    };
    return result;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = MySqlSource.sshWrappedSource();
    LOGGER.info("starting source: {}", MySqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MySqlSource.class);
  }

  public enum ReplicationMethod {
    STANDARD,
    CDC
  }

}
