/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static io.airbyte.cdk.db.jdbc.JdbcUtils.EQUALS;
import static io.airbyte.cdk.integrations.debezium.AirbyteDebeziumHandler.isAnyStreamIncrementalSyncMode;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_DELETED_AT;
import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_UPDATED_AT;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcDataSourceUtils.DEFAULT_JDBC_PARAMETERS_DELIMITER;
import static io.airbyte.cdk.integrations.source.jdbc.JdbcDataSourceUtils.assertCustomParametersDontOverwriteDefaultParameters;
import static io.airbyte.integrations.source.mysql.MySqlQueryUtils.getCursorBasedSyncStatusForStreams;
import static io.airbyte.integrations.source.mysql.MySqlQueryUtils.getTableSizeInfoForStreams;
import static io.airbyte.integrations.source.mysql.MySqlQueryUtils.logStreamSyncStatus;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.convertNameNamespacePairFromV0;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.filterStreamInIncrementalMode;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.getMySqlFullRefreshInitialLoadHandler;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.getMySqlInitialLoadGlobalStateManager;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.initPairToPrimaryKeyInfoMap;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.isSavedOffsetStillPresentOnServer;
import static io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.streamsForInitialPrimaryKeyLoad;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.mysql.cj.MysqlType;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.Source;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveSourceRunner;
import io.airbyte.cdk.integrations.base.ssh.SshWrappedSource;
import io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil;
import io.airbyte.cdk.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.cdk.integrations.source.jdbc.JdbcDataSourceUtils;
import io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils;
import io.airbyte.cdk.integrations.source.jdbc.JdbcSSLConnectionUtils.SslMode;
import io.airbyte.cdk.integrations.source.relationaldb.DbSourceDiscoverUtil;
import io.airbyte.cdk.integrations.source.relationaldb.InitialLoadHandler;
import io.airbyte.cdk.integrations.source.relationaldb.TableInfo;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateGeneratorUtils;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManagerFactory;
import io.airbyte.cdk.integrations.source.relationaldb.streamstatus.StreamStatusTraceEmitterIterator;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.source.mysql.cdc.CdcConfigurationHelper;
import io.airbyte.integrations.source.mysql.cursor_based.MySqlCursorBasedStateManager;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadGlobalStateManager;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadHandler;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStateManager;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialLoadStreamStateManager;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.CursorBasedStreams;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mysql.internal.models.CursorBasedStatus;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.jetbrains.annotations.NotNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlSource extends AbstractJdbcSource<MysqlType> implements Source {

  public static final String TUNNEL_METHOD = "tunnel_method";
  public static final String NO_TUNNEL = "NO_TUNNEL";
  public static final String SSL_MODE = "ssl_mode";
  private static final String MODE = "mode";
  public static final String SSL_MODE_PREFERRED = "preferred";
  public static final String SSL_MODE_REQUIRED = "required";

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
  public static final String CDC_LOG_FILE = "_ab_cdc_log_file";
  public static final String CDC_LOG_POS = "_ab_cdc_log_pos";
  public static final String CDC_DEFAULT_CURSOR = "_ab_cdc_cursor";

  public static Source sshWrappedSource(final MySqlSource source) {
    return new SshWrappedSource(source, JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  private ConnectorSpecification getCloudDeploymentSpec(final ConnectorSpecification originalSpec) {
    final ConnectorSpecification spec = Jsons.clone(originalSpec);
    // Remove the SSL options
    ((ObjectNode) spec.getConnectionSpecification().get("properties")).remove(JdbcUtils.SSL_KEY);
    // Set SSL_MODE to required by default
    ((ObjectNode) spec.getConnectionSpecification().get("properties").get(SSL_MODE)).put("default", SSL_MODE_REQUIRED);
    return spec;
  }

  @Override
  public @NotNull ConnectorSpecification spec() throws Exception {
    if (cloudDeploymentMode()) {
      return getCloudDeploymentSpec(super.spec());
    }
    return super.spec();
  }

  @Override
  public AirbyteConnectionStatus check(final @NotNull JsonNode config) throws Exception {
    // #15808 Disallow connecting to db with disable, prefer or allow SSL mode when connecting directly
    // and not over SSH tunnel
    if (cloudDeploymentMode()) {
      if (config.has(TUNNEL_METHOD)
          && config.get(TUNNEL_METHOD).has(TUNNEL_METHOD)
          && config.get(TUNNEL_METHOD).get(TUNNEL_METHOD).asText().equals(NO_TUNNEL)) {
        // If no SSH tunnel
        if (config.has(SSL_MODE) && config.get(SSL_MODE).has(MODE)) {
          if (Set.of(SSL_MODE_PREFERRED).contains(config.get(SSL_MODE).get(MODE).asText())) {
            // Fail in case SSL mode is preferred
            return new AirbyteConnectionStatus()
                .withStatus(Status.FAILED)
                .withMessage(
                    "Unsecured connection not allowed. If no SSH Tunnel set up, please use one of the following SSL modes: required, verify-ca, verify-identity");
          }
        }
      }
    }
    return super.check(config);
  }

  public MySqlSource() {
    super(DRIVER_CLASS, MySqlStreamingQueryConfig::new, new MySqlSourceOperations());
  }

  @Override
  public boolean supportResumableFullRefresh(final JdbcDatabase database, final ConfiguredAirbyteStream airbyteStream) {
    if (airbyteStream.getStream() != null && airbyteStream.getStream().getSourceDefinedPrimaryKey() != null
        && !airbyteStream.getStream().getSourceDefinedPrimaryKey().isEmpty()) {
      return true;
    }

    return false;
  }

  private MySqlInitialLoadStateManager initialLoadStateManager = null;
  private boolean isSavedOffsetStillPresentOnServer = false;

  @Override
  protected void initializeForStateManager(final JdbcDatabase database,
                                           final @NotNull ConfiguredAirbyteCatalog catalog,
                                           final @NotNull Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
                                           final @NotNull StateManager stateManager) {
    if (initialLoadStateManager != null) {
      return;
    }
    final var sourceConfig = database.getSourceConfig();

    if (isCdc(sourceConfig)) {
      isSavedOffsetStillPresentOnServer = isSavedOffsetStillPresentOnServer(database, catalog, stateManager);
      initialLoadStateManager = getMySqlInitialLoadGlobalStateManager(database, catalog, stateManager, tableNameToTable, getQuoteString(),
          isSavedOffsetStillPresentOnServer);
    } else {
      final MySqlCursorBasedStateManager cursorBasedStateManager = new MySqlCursorBasedStateManager(stateManager.getRawStateMessages(), catalog);
      final InitialLoadStreams initialLoadStreams = streamsForInitialPrimaryKeyLoad(cursorBasedStateManager, catalog);
      initialLoadStateManager =
          new MySqlInitialLoadStreamStateManager(catalog, initialLoadStreams,
              initPairToPrimaryKeyInfoMap(database, initialLoadStreams, tableNameToTable, getQuoteString()));
    }
  }

  @Override
  public InitialLoadHandler<MysqlType> getInitialLoadHandler(final JdbcDatabase database,
                                                             final ConfiguredAirbyteStream stream,
                                                             final ConfiguredAirbyteCatalog catalog,
                                                             final StateManager stateManager) {

    var sourceConfig = database.getSourceConfig();

    if (isCdc(sourceConfig)) {
      return getMySqlFullRefreshInitialLoadHandler(database, catalog, (MySqlInitialLoadGlobalStateManager) initialLoadStateManager, stateManager,
          stream, Instant.now(), getQuoteString(), isSavedOffsetStillPresentOnServer)
              .get();
    } else {
      return new MySqlInitialLoadHandler(sourceConfig, database, new MySqlSourceOperations(), getQuoteString(), initialLoadStateManager,
          Optional.empty(),
          getTableSizeInfoForStreams(database, catalog.getStreams(), getQuoteString()));
    }
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

  /*
   * To prepare for Destination v2, cdc streams must have a default cursor field Cursor format: the
   * airbyte [emittedAt(converted to nano seconds)] + [sync wide record counter]
   */
  private static AirbyteStream setDefaultCursorFieldForCdc(final AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setDefaultCursorField(ImmutableList.of(CDC_DEFAULT_CURSOR));
    }
    return stream;
  }

  // Note: in place mutation.
  private static AirbyteStream addCdcMetadataColumns(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    final JsonNode airbyteIntegerType = Jsons.jsonNode(ImmutableMap.of("type", "number", "airbyte_type", "integer"));
    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LOG_FILE, stringType);
    properties.set(CDC_LOG_POS, numberType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);
    properties.set(CDC_DEFAULT_CURSOR, airbyteIntegerType);

    return stream;
  }

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config) throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(super.getCheckOperations(config));
    if (isCdc(config)) {
      checkOperations.addAll(CdcConfigurationHelper.getCheckOperations());

      checkOperations.add(database -> {
        RecordWaitTimeUtil.checkFirstRecordWaitTime(config);
        CdcConfigurationHelper.checkServerTimeZoneConfig(config);
      });
    }
    return checkOperations;
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) {
    final AirbyteCatalog catalog = super.discover(config);

    if (isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(MySqlSource::overrideSyncModes)
          .map(MySqlSource::removeIncrementalWithoutPk)
          .map(MySqlSource::setIncrementalToSourceDefined)
          .map(MySqlSource::setDefaultCursorFieldForCdc)
          .map(MySqlSource::addCdcMetadataColumns)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public Collection<AutoCloseableIterator<AirbyteMessage>> readStreams(final JsonNode config,
                                                                       final ConfiguredAirbyteCatalog catalog,
                                                                       final JsonNode state)
      throws Exception {
    final AirbyteStateType supportedStateType = getSupportedStateType(config);
    final StateManager stateManager =
        StateManagerFactory.createStateManager(supportedStateType,
            StateGeneratorUtils.deserializeInitialState(state, supportedStateType), catalog);
    final Instant emittedAt = Instant.now();

    final JdbcDatabase database = createDatabase(config);

    logPreSyncDebugData(database, catalog);

    final Map<String, TableInfo<CommonField<MysqlType>>> fullyQualifiedTableNameToInfo =
        discoverWithoutSystemTables(database)
            .stream()
            .collect(Collectors.toMap(t -> String.format("%s.%s", t.getNameSpace(), t.getName()),
                Function
                    .identity()));

    validateCursorFieldForIncrementalTables(fullyQualifiedTableNameToInfo, catalog, database);

    initializeForStateManager(database, catalog, fullyQualifiedTableNameToInfo, stateManager);

    DbSourceDiscoverUtil.logSourceSchemaChange(fullyQualifiedTableNameToInfo, catalog, this::getAirbyteType);

    final List<AutoCloseableIterator<AirbyteMessage>> incrementalIterators =
        getIncrementalIterators(database, catalog, fullyQualifiedTableNameToInfo, stateManager,
            emittedAt);
    final List<AutoCloseableIterator<AirbyteMessage>> fullRefreshIterators =
        getFullRefreshIterators(database, catalog, fullyQualifiedTableNameToInfo, stateManager,
            emittedAt);
    final List<AutoCloseableIterator<AirbyteMessage>> iteratorList = Stream
        .of(incrementalIterators, fullRefreshIterators)
        .flatMap(Collection::stream)
        .collect(Collectors.toList());

    return iteratorList;
  }

  @Override
  protected void logPreSyncDebugData(final JdbcDatabase database, final ConfiguredAirbyteCatalog catalog)
      throws SQLException {
    super.logPreSyncDebugData(database, catalog);
    final Set<String> streamNames = new HashSet<>();
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      streamNames.add(stream.getStream().getName());
    }
    final Set<String> storageEngines = MySqlQueryUtils.getStorageEngines(database, streamNames);
    LOGGER.info(String.format("Detected the following storage engines for MySQL: %s", storageEngines.toString()));
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final String encodedDatabaseName = URLEncoder.encode(config.get(JdbcUtils.DATABASE_KEY).asText(), StandardCharsets.UTF_8);
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        encodedDatabaseName));

    // To fetch the result in batches, the "useCursorFetch=true" must be set.
    // https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-implementation-notes.html.
    // When using this approach MySql creates a temporary table which may have some effect on db
    // performance.
    jdbcUrl.append("?useCursorFetch=true");
    // What should happen when the driver encounters DATETIME values that are composed entirely of zeros
    // https://dev.mysql.com/doc/connector-j/8.1/en/connector-j-connp-props-datetime-types-processing.html#cj-conn-prop_zeroDateTimeBehavior
    jdbcUrl.append("&zeroDateTimeBehavior=CONVERT_TO_NULL");
    // ensure the return tinyint(1) is boolean
    jdbcUrl.append("&tinyInt1isBit=true");
    // ensure the return year value is a Date; see the rationale
    // in the setJsonField method in MySqlSourceOperations.java
    jdbcUrl.append("&yearIsDateType=false");
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
    return isCdc(config) ? AirbyteStateType.GLOBAL : AirbyteStateType.STREAM;
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<MysqlType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {

    final JsonNode sourceConfig = database.getSourceConfig();
    if (isCdc(sourceConfig) && isAnyStreamIncrementalSyncMode(catalog)) {
      LOGGER.info("Using PK + CDC");
      return MySqlInitialReadUtil.getCdcReadIterators(database, catalog, tableNameToTable, stateManager,
          (MySqlInitialLoadGlobalStateManager) initialLoadStateManager, emittedAt,
          getQuoteString(), isSavedOffsetStillPresentOnServer);
    } else {
      if (isAnyStreamIncrementalSyncMode(catalog)) {
        LOGGER.info("Syncing via Primary Key");
        final MySqlCursorBasedStateManager cursorBasedStateManager = new MySqlCursorBasedStateManager(stateManager.getRawStateMessages(), catalog);
        final InitialLoadStreams initialLoadStreams =
            filterStreamInIncrementalMode(streamsForInitialPrimaryKeyLoad(cursorBasedStateManager, catalog));
        final Map<AirbyteStreamNameNamespacePair, CursorBasedStatus> pairToCursorBasedStatus =
            getCursorBasedSyncStatusForStreams(database, initialLoadStreams.streamsForInitialLoad(), stateManager, getQuoteString());
        final CursorBasedStreams cursorBasedStreams =
            new CursorBasedStreams(MySqlInitialReadUtil.identifyStreamsForCursorBased(catalog, initialLoadStreams.streamsForInitialLoad()),
                pairToCursorBasedStatus);

        logStreamSyncStatus(initialLoadStreams.streamsForInitialLoad(), "Primary Key");
        logStreamSyncStatus(cursorBasedStreams.streamsForCursorBased(), "Cursor");

        final MySqlInitialLoadHandler initialLoadHandler =
            new MySqlInitialLoadHandler(sourceConfig, database, new MySqlSourceOperations(), getQuoteString(), initialLoadStateManager,
                Optional.of(namespacePair -> Jsons.jsonNode(pairToCursorBasedStatus.get(convertNameNamespacePairFromV0(namespacePair)))),
                getTableSizeInfoForStreams(database, catalog.getStreams(), getQuoteString()));
        // Cursor based incremental iterators are decorated with start and complete status traces
        final List<AutoCloseableIterator<AirbyteMessage>> initialLoadIterator = new ArrayList<>(initialLoadHandler.getIncrementalIterators(
            new ConfiguredAirbyteCatalog().withStreams(initialLoadStreams.streamsForInitialLoad()),
            tableNameToTable,
            emittedAt, true, true));

        // Build Cursor based iterator
        final List<AutoCloseableIterator<AirbyteMessage>> cursorBasedIterator =
            new ArrayList<>(super.getIncrementalIterators(database,
                new ConfiguredAirbyteCatalog().withStreams(
                    cursorBasedStreams.streamsForCursorBased()),
                tableNameToTable,
                cursorBasedStateManager, emittedAt));

        return Stream.of(initialLoadIterator, cursorBasedIterator).flatMap(Collection::stream).collect(Collectors.toList());
      }
    }

    LOGGER.info("using CDC: {}", false);
    return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager,
        emittedAt);
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

  private boolean cloudDeploymentMode() {
    return AdaptiveSourceRunner.CLOUD_MODE.equalsIgnoreCase(getFeatureFlags().deploymentMode());
  }

  @Override
  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  public static String toSslJdbcParam(final SslMode sslMode) {
    final var result = switch (sslMode) {
      case DISABLED, PREFERRED, REQUIRED, VERIFY_CA, VERIFY_IDENTITY -> sslMode.name();
      default -> throw new IllegalArgumentException("unexpected ssl mode");
    };
    return result;
  }

  @Override
  public JdbcDatabase createDatabase(final JsonNode sourceConfig) throws SQLException {
    // return super.createDatabase(sourceConfig, this::getConnectionProperties);
    final JsonNode jdbcConfig = toDatabaseConfig(sourceConfig);
    final Map<String, String> connectionProperties = this.getConnectionProperties(sourceConfig);
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

    setQuoteString((getQuoteString() == null ? database.getMetaData().getIdentifierQuoteString() : getQuoteString()));
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(jdbcConfig);
    return database;
  }

  public Map<String, String> getConnectionProperties(final JsonNode config) {
    final Map<String, String> customProperties =
        config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)
            ? parseJdbcParameters(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText(), DEFAULT_JDBC_PARAMETERS_DELIMITER)
            : new HashMap<>();
    final Map<String, String> defaultProperties = JdbcDataSourceUtils.getDefaultConnectionProperties(config);
    assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties);
    return MoreMaps.merge(customProperties, defaultProperties);
  }

  public static Map<String, String> parseJdbcParameters(final String jdbcPropertiesString, final String delimiter) {
    final Map<String, String> parameters = new HashMap<>();
    if (!jdbcPropertiesString.isBlank()) {
      final String[] keyValuePairs = jdbcPropertiesString.split(delimiter);
      for (final String kv : keyValuePairs) {
        final String[] split = kv.split("=");
        if (split.length == 2) {
          parameters.put(split[0], split[1]);
        } else if (split.length == 3 && kv.contains("sessionVariables")) {
          parameters.put(split[0], split[1] + "=" + split[2]);
        } else {
          throw new ConfigErrorException(
              "jdbc_url_params must be formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3). Got "
                  + jdbcPropertiesString);
        }
      }
    }
    return parameters;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = MySqlSource.sshWrappedSource(new MySqlSource());
    LOGGER.info("starting source: {}", MySqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MySqlSource.class);
  }

  public enum ReplicationMethod {
    STANDARD,
    CDC
  }

  @NotNull
  @Override
  public AutoCloseableIterator<AirbyteMessage> augmentWithStreamStatus(@NotNull final ConfiguredAirbyteStream airbyteStream,
                                                                       @NotNull final AutoCloseableIterator<AirbyteMessage> streamItrator) {
    final var pair =
        new io.airbyte.protocol.models.AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
    final var starterStatus =
        new StreamStatusTraceEmitterIterator(new AirbyteStreamStatusHolder(pair, AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.STARTED));
    final var completeStatus =
        new StreamStatusTraceEmitterIterator(new AirbyteStreamStatusHolder(pair, AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE));
    return AutoCloseableIterators.concatWithEagerClose(starterStatus, streamItrator, completeStatus);
  }

}
