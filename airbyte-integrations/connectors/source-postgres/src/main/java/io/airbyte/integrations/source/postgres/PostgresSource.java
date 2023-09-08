/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.db.jdbc.JdbcConstants.JDBC_COLUMN_COLUMN_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_INDEX_NAME;
import static io.airbyte.db.jdbc.JdbcConstants.JDBC_INDEX_NON_UNIQUE;
import static io.airbyte.db.jdbc.JdbcUtils.AMPERSAND;
import static io.airbyte.db.jdbc.JdbcUtils.EQUALS;
import static io.airbyte.db.jdbc.JdbcUtils.PLATFORM_DATA_INCREASE_FACTOR;
import static io.airbyte.integrations.debezium.AirbyteDebeziumHandler.shouldUseCDC;
import static io.airbyte.integrations.source.jdbc.JdbcDataSourceUtils.DEFAULT_JDBC_PARAMETERS_DELIMITER;
import static io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_PASS;
import static io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils.CLIENT_KEY_STORE_URL;
import static io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils.PARAM_CA_CERTIFICATE;
import static io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils.parseSSLConfig;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.NULL_CURSOR_VALUE_NO_SCHEMA_QUERY;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.ROW_COUNT_RESULT_COL;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.TABLE_ESTIMATE_QUERY;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.TOTAL_BYTES_RESULT_COL;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.filterStreamsUnderVacuumForCtidSync;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.getCursorBasedSyncStatusForStreams;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.streamsUnderVacuum;
import static io.airbyte.integrations.source.postgres.PostgresUtils.isAnyStreamIncrementalSyncMode;
import static io.airbyte.integrations.source.postgres.PostgresUtils.prettyPrintConfiguredAirbyteStreamList;
import static io.airbyte.integrations.source.postgres.cdc.PostgresCdcCtidInitializer.cdcCtidIteratorsCombined;
import static io.airbyte.integrations.source.postgres.cursor_based.CursorBasedCtidUtils.categoriseStreams;
import static io.airbyte.integrations.source.postgres.cursor_based.CursorBasedCtidUtils.reclassifyCategorisedCtidStreams;
import static io.airbyte.integrations.source.postgres.xmin.XminCtidUtils.categoriseStreams;
import static io.airbyte.integrations.source.postgres.xmin.XminCtidUtils.reclassifyCategorisedCtidStreams;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.PARAM_SSL_MODE;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import datadog.trace.api.Trace;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.internals.postgres.PostgresReplicationConnection;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.JdbcDataSourceUtils;
import io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils;
import io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils.SslMode;
import io.airbyte.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils.ResultWithFailed;
import io.airbyte.integrations.source.postgres.PostgresQueryUtils.TableBlockSize;
import io.airbyte.integrations.source.postgres.ctid.CtidPerStreamStateManager;
import io.airbyte.integrations.source.postgres.ctid.CtidPostgresSourceOperations;
import io.airbyte.integrations.source.postgres.ctid.CtidStateManager;
import io.airbyte.integrations.source.postgres.ctid.CtidUtils.StreamsCategorised;
import io.airbyte.integrations.source.postgres.ctid.FileNodeHandler;
import io.airbyte.integrations.source.postgres.ctid.PostgresCtidHandler;
import io.airbyte.integrations.source.postgres.cursor_based.CursorBasedCtidUtils.CursorBasedStreams;
import io.airbyte.integrations.source.postgres.cursor_based.PostgresCursorBasedStateManager;
import io.airbyte.integrations.source.postgres.internal.models.CursorBasedStatus;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.integrations.source.postgres.xmin.PostgresXminHandler;
import io.airbyte.integrations.source.postgres.xmin.XminCtidUtils.XminStreams;
import io.airbyte.integrations.source.postgres.xmin.XminStateManager;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteEstimateTraceMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSource extends AbstractJdbcSource<PostgresType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSource.class);
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;
  public static final String PARAM_SSLMODE = "sslmode";
  public static final String SSL_MODE = "ssl_mode";
  public static final String SSL_ROOT_CERT = "sslrootcert";

  static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();
  public static final String CA_CERTIFICATE_PATH = "ca_certificate_path";
  public static final String SSL_KEY = "sslkey";
  public static final String SSL_PASSWORD = "sslpassword";
  public static final String MODE = "mode";

  private List<String> schemas;

  private Set<AirbyteStreamNameNamespacePair> publicizedTablesInCdc;
  private final FeatureFlags featureFlags;
  private static final Set<String> INVALID_CDC_SSL_MODES = ImmutableSet.of("allow", "prefer");
  private int stateEmissionFrequency;
  private XminStatus xminStatus;

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new PostgresSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY, "security");
  }

  PostgresSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new PostgresSourceOperations());
    this.featureFlags = new EnvVariableFeatureFlags();
    this.stateEmissionFrequency = INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final List<String> additionalParameters = new ArrayList<>();
    // Initialize parameters with prepareThreshold=0 to mitigate pgbouncer errors
    // https://github.com/airbytehq/airbyte/issues/24796
    additionalParameters.add("prepareThreshold=0");

    final String encodedDatabaseName = HostPortResolver.encodeValue(config.get(JdbcUtils.DATABASE_KEY).asText());

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:postgresql://%s:%s/%s?",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        encodedDatabaseName));

    if (config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      jdbcUrl.append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText()).append(AMPERSAND);
    }

    final Map<String, String> sslParameters = parseSSLConfig(config);
    if (config.has(PARAM_SSL_MODE) && config.get(PARAM_SSL_MODE).has(PARAM_CA_CERTIFICATE)) {
      sslParameters.put(CA_CERTIFICATE_PATH,
          JdbcSSLConnectionUtils.fileFromCertPem(config.get(PARAM_SSL_MODE).get(PARAM_CA_CERTIFICATE).asText()).toString());
      LOGGER.debug("root ssl ca crt file: {}", sslParameters.get(CA_CERTIFICATE_PATH));
    }

    if (config.has(JdbcUtils.SCHEMAS_KEY) && config.get(JdbcUtils.SCHEMAS_KEY).isArray()) {
      schemas = new ArrayList<>();
      for (final JsonNode schema : config.get(JdbcUtils.SCHEMAS_KEY)) {
        schemas.add(schema.asText());
      }
    }

    if (schemas != null && !schemas.isEmpty()) {
      additionalParameters.add("currentSchema=" + String.join(",", schemas));
    }

    additionalParameters.forEach(x -> jdbcUrl.append(x).append("&"));

    jdbcUrl.append(toJDBCQueryParams(sslParameters));
    LOGGER.debug("jdbc url: {}", jdbcUrl);
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    configBuilder.putAll(sslParameters);
    return Jsons.jsonNode(configBuilder.build());
  }

  public String toJDBCQueryParams(final Map<String, String> sslParams) {
    return Objects.isNull(sslParams) ? ""
        : sslParams.entrySet()
            .stream()
            .map((entry) -> {
              try {
                return switch (entry.getKey()) {
                  case JdbcSSLConnectionUtils.SSL_MODE -> PARAM_SSLMODE + EQUALS + toSslJdbcParam(SslMode.valueOf(entry.getValue()));
                  case CA_CERTIFICATE_PATH -> SSL_ROOT_CERT + EQUALS + entry.getValue();
                  case CLIENT_KEY_STORE_URL -> SSL_KEY + EQUALS + Path.of(new URI(entry.getValue()));
                  case CLIENT_KEY_STORE_PASS -> SSL_PASSWORD + EQUALS + entry.getValue();
                  default -> "";
                };
              } catch (final URISyntaxException e) {
                throw new IllegalArgumentException("unable to convert to URI", e);
              }
            })
            .filter(s -> Objects.nonNull(s) && !s.isEmpty())
            .collect(Collectors.joining(JdbcUtils.AMPERSAND));
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of("information_schema", "pg_catalog", "pg_internal", "catalog_history");
  }

  @Override
  protected Set<String> getExcludedViews() {
    return Set.of("pg_stat_statements", "pg_stat_statements_info", "pg_buffercache");
  }

  @Override
  protected void logPreSyncDebugData(final JdbcDatabase database, final ConfiguredAirbyteCatalog catalog)
      throws SQLException {
    super.logPreSyncDebugData(database, catalog);
    for (final ConfiguredAirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getStream().getName();
      final String schemaName = stream.getStream().getNamespace();
      final ResultSet indexInfo = database.getMetaData().getIndexInfo(null,
          schemaName,
          streamName,
          false,
          false);
      LOGGER.info("Discovering indexes for schema \"{}\", table \"{}\"", schemaName, streamName);
      while (indexInfo.next()) {
        LOGGER.info("Index name: {}, Column: {}, Unique: {}",
            indexInfo.getString(JDBC_INDEX_NAME),
            indexInfo.getString(JDBC_COLUMN_COLUMN_NAME),
            !indexInfo.getBoolean(JDBC_INDEX_NON_UNIQUE));
      }
      indexInfo.close();
    }

    // Log and save the xmin status
    this.xminStatus = PostgresQueryUtils.getXminStatus(database);
    LOGGER.info(String.format("Xmin Status : {Number of wraparounds: %s, Xmin Transaction Value: %s, Xmin Raw Value: %s",
        xminStatus.getNumWraparound(), xminStatus.getXminXidValue(), xminStatus.getXminRawValue()));

  }

  @Override
  @Trace(operationName = DISCOVER_TRACE_OPERATION_NAME)
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    final AirbyteCatalog catalog = super.discover(config);

    if (PostgresUtils.isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(PostgresCatalogHelper::overrideSyncModes)
          .map(PostgresCatalogHelper::removeIncrementalWithoutPk)
          .map(PostgresCatalogHelper::setIncrementalToSourceDefined)
          .map(PostgresCatalogHelper::setDefaultCursorFieldForCdc)
          .map(PostgresCatalogHelper::addCdcMetadataColumns)
          // If we're in CDC mode and a stream is not in the publication, the user should only be able to sync
          // this in FULL_REFRESH mode
          .map(stream -> PostgresCatalogHelper.setFullRefreshForNonPublicationStreams(stream, publicizedTablesInCdc))
          .collect(toList());

      catalog.setStreams(streams);
    } else if (PostgresUtils.isXmin(config)) {
      // Xmin replication has a source-defined cursor (the xmin column). This is done to prevent the user
      // from being able to pick their own cursor.
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(PostgresCatalogHelper::overrideSyncModes)
          .map(PostgresCatalogHelper::setIncrementalToSourceDefined)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public JdbcDatabase createDatabase(final JsonNode sourceConfig) throws SQLException {
    final JsonNode jdbcConfig = toDatabaseConfig(sourceConfig);
    // Create the data source
    final DataSource dataSource = DataSourceFactory.create(
        jdbcConfig.has(JdbcUtils.USERNAME_KEY) ? jdbcConfig.get(JdbcUtils.USERNAME_KEY).asText() : null,
        jdbcConfig.has(JdbcUtils.PASSWORD_KEY) ? jdbcConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        driverClass,
        jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText(),
        getConnectionProperties(sourceConfig));
    // Record the data source so that it can be closed.
    dataSources.add(dataSource);

    final JdbcDatabase database = new StreamingJdbcDatabase(
        dataSource,
        sourceOperations,
        streamingQueryConfigProvider);

    quoteString = (quoteString == null ? database.getMetaData().getIdentifierQuoteString() : quoteString);
    database.setSourceConfig(sourceConfig);
    database.setDatabaseConfig(jdbcConfig);

    this.publicizedTablesInCdc = PostgresCatalogHelper.getPublicizedTables(database);

    return database;
  }

  public static Map<String, String> getConnectionProperties(final JsonNode config) {
    final Map<String, String> customProperties =
        config.has(JdbcUtils.JDBC_URL_PARAMS_KEY)
            ? parseJdbcParameters(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText(), DEFAULT_JDBC_PARAMETERS_DELIMITER)
            : new HashMap<>();
    final Map<String, String> defaultProperties = JdbcDataSourceUtils.getDefaultConnectionProperties(config);
    JdbcDataSourceUtils.assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties);
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
        } else if (split.length > 2 && "options".equals(split[0])) {
          parameters.put(split[0], kv.substring(split[0].length() + delimiter.length()));
        } else {
          throw new ConfigErrorException(
              "jdbc_url_params must be formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3). Got "
                  + jdbcPropertiesString);
        }
      }
    }
    return parameters;
  }

  @Override
  public List<TableInfo<CommonField<PostgresType>>> discoverInternal(final JdbcDatabase database) throws Exception {
    return discoverRawTables(database);
  }

  public List<TableInfo<CommonField<PostgresType>>> discoverRawTables(final JdbcDatabase database) throws Exception {
    if (schemas != null && !schemas.isEmpty()) {
      // process explicitly selected (from UI) schemas
      final List<TableInfo<CommonField<PostgresType>>> internals = new ArrayList<>();
      for (final String schema : schemas) {
        LOGGER.debug("Checking schema: {}", schema);
        final List<TableInfo<CommonField<PostgresType>>> tables = super.discoverInternal(database, schema);
        internals.addAll(tables);
        for (final TableInfo<CommonField<PostgresType>> table : tables) {
          LOGGER.debug("Found table: {}.{}", table.getNameSpace(), table.getName());
        }
      }
      return internals;
    } else {
      LOGGER.info("No schemas explicitly set on UI to process, so will process all of existing schemas in DB");
      return super.discoverInternal(database);
    }
  }

  @VisibleForTesting
  List<JsonNode> getReplicationSlot(final JdbcDatabase database, final JsonNode config) {
    try {
      return database.queryJsons(connection -> {
        final String sql = "SELECT * FROM pg_replication_slots WHERE slot_name = ? AND plugin = ? AND database = ?";
        final PreparedStatement ps = connection.prepareStatement(sql);
        ps.setString(1, config.get("replication_method").get("replication_slot").asText());
        ps.setString(2, PostgresUtils.getPluginValue(config.get("replication_method")));
        ps.setString(3, config.get(JdbcUtils.DATABASE_KEY).asText());

        LOGGER.info("Attempting to find the named replication slot using the query: {}", ps);

        return ps;
      }, sourceOperations::rowToJson);
    } catch (final SQLException e) {
      throw new RuntimeException(e);
    }
  }

  @Trace(operationName = CHECK_TRACE_OPERATION_NAME)
  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config)
      throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(
        super.getCheckOperations(config));

    if (PostgresUtils.isCdc(config)) {
      checkOperations.add(database -> {
        final List<JsonNode> matchingSlots = getReplicationSlot(database, config);

        if (matchingSlots.size() != 1) {
          throw new ConfigErrorException(
              "Expected exactly one replication slot but found " + matchingSlots.size()
                  + ". Please read the docs and add a replication slot to your database.");
        }

      });

      checkOperations.add(database -> {
        final List<JsonNode> matchingPublications = database.queryJsons(connection -> {
          final PreparedStatement ps = connection.prepareStatement("SELECT * FROM pg_publication WHERE pubname = ?");
          ps.setString(1, config.get("replication_method").get("publication").asText());
          LOGGER.info("Attempting to find the publication using the query: " + ps);
          return ps;
        }, sourceOperations::rowToJson);

        if (matchingPublications.size() != 1) {
          throw new ConfigErrorException(
              "Expected exactly one publication but found " + matchingPublications.size()
                  + ". Please read the docs and add a publication to your database.");
        }

      });

      checkOperations.add(database -> PostgresUtils.checkFirstRecordWaitTime(config));

      checkOperations.add(database -> PostgresUtils.checkQueueSize(config));

      // Verify that a CDC connection can be created
      checkOperations.add(database -> {
        /**
         * TODO: Next line is required for SSL connections so the JDBC_URL is set with all required
         * parameters. This needs to be handle by createConnection function instead. Created issue
         * https://github.com/airbytehq/airbyte/issues/23380.
         */
        final JsonNode databaseConfig = database.getDatabaseConfig();
        // Empty try statement as we only need to verify that the connection can be created.
        try (final Connection connection = PostgresReplicationConnection.createConnection(databaseConfig)) {}
      });
    }

    return checkOperations;
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (PostgresUtils.isCdc(sourceConfig) && shouldUseCDC(catalog)) {
      LOGGER.info("Using ctid + CDC");
      return cdcCtidIteratorsCombined(database, catalog, tableNameToTable, stateManager, emittedAt, getQuoteString(),
          getReplicationSlot(database, sourceConfig).get(0));
    }

    if (isAnyStreamIncrementalSyncMode(catalog) && PostgresUtils.isXmin(sourceConfig)) {
      final StreamsCategorised<XminStreams> streamsCategorised = categoriseStreams(stateManager, catalog, xminStatus);
      final ResultWithFailed<List<AirbyteStreamNameNamespacePair>> streamsUnderVacuum = streamsUnderVacuum(database,
          streamsCategorised.ctidStreams().streamsForCtidSync(),
          getQuoteString());

      // Streams we failed to query for Vacuum - such as in the case of an unsupported postgres server
      // are reclassified as xmin since we cannot guarantee that ctid will be possible.
      reclassifyCategorisedCtidStreams(streamsCategorised, streamsUnderVacuum.failed());

      List<ConfiguredAirbyteStream> finalListOfStreamsToBeSyncedViaCtid =
          filterStreamsUnderVacuumForCtidSync(streamsUnderVacuum.result(), streamsCategorised.ctidStreams());
      final FileNodeHandler fileNodeHandler =
          PostgresQueryUtils.fileNodeForStreams(database,
              finalListOfStreamsToBeSyncedViaCtid,
              getQuoteString());

      // In case we failed to query for fileNode, streams will get reclassified as xmin
      if (!fileNodeHandler.getFailedToQuery().isEmpty()) {
        reclassifyCategorisedCtidStreams(streamsCategorised, fileNodeHandler.getFailedToQuery());
        finalListOfStreamsToBeSyncedViaCtid =
            filterStreamsUnderVacuumForCtidSync(streamsUnderVacuum.result(), streamsCategorised.ctidStreams());
      }

      final CtidStateManager ctidStateManager = new CtidPerStreamStateManager(streamsCategorised.ctidStreams().statesFromCtidSync(), fileNodeHandler);
      final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes =
          PostgresQueryUtils.getTableBlockSizeForStreams(
              database,
              finalListOfStreamsToBeSyncedViaCtid,
              getQuoteString());

      if (!streamsCategorised.ctidStreams().streamsForCtidSync().isEmpty()) {
        LOGGER.info("Streams to be synced via ctid : {}", finalListOfStreamsToBeSyncedViaCtid.size());
        LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(finalListOfStreamsToBeSyncedViaCtid));
      } else {
        LOGGER.info("No Streams will be synced via ctid.");
      }

      if (!streamsCategorised.remainingStreams().streamsForXminSync().isEmpty()) {
        LOGGER.info("Streams to be synced via xmin : {}", streamsCategorised.remainingStreams().streamsForXminSync().size());
        LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(streamsCategorised.remainingStreams().streamsForXminSync()));
      } else {
        LOGGER.info("No Streams will be synced via xmin.");
      }

      final XminStateManager xminStateManager = new XminStateManager(streamsCategorised.remainingStreams().statesFromXminSync());
      final PostgresXminHandler xminHandler = new PostgresXminHandler(database, sourceOperations, getQuoteString(), xminStatus, xminStateManager);

      final PostgresCtidHandler ctidHandler =
          new PostgresCtidHandler(sourceConfig, database, new CtidPostgresSourceOperations(Optional.empty()), getQuoteString(),
              fileNodeHandler, tableBlockSizes, ctidStateManager,
              namespacePair -> Jsons.jsonNode(xminStatus));

      final List<AutoCloseableIterator<AirbyteMessage>> initialSyncCtidIterators = new ArrayList<>(ctidHandler.getInitialSyncCtidIterator(
          new ConfiguredAirbyteCatalog().withStreams(finalListOfStreamsToBeSyncedViaCtid), tableNameToTable, emittedAt));
      final List<AutoCloseableIterator<AirbyteMessage>> xminIterators = new ArrayList<>(xminHandler.getIncrementalIterators(
          new ConfiguredAirbyteCatalog().withStreams(streamsCategorised.remainingStreams().streamsForXminSync()), tableNameToTable, emittedAt));

      return Stream
          .of(initialSyncCtidIterators, xminIterators)
          .flatMap(Collection::stream)
          .collect(Collectors.toList());

    } else if (isAnyStreamIncrementalSyncMode(catalog)) {
      final PostgresCursorBasedStateManager postgresCursorBasedStateManager =
          new PostgresCursorBasedStateManager(stateManager.getRawStateMessages(), catalog);
      final StreamsCategorised<CursorBasedStreams> streamsCategorised = categoriseStreams(postgresCursorBasedStateManager, catalog);
      final ResultWithFailed<List<AirbyteStreamNameNamespacePair>> streamsUnderVacuum = streamsUnderVacuum(database,
          streamsCategorised.ctidStreams().streamsForCtidSync(),
          getQuoteString());

      // Streams we failed to query for Vacuum - such as in the case of an unsupported postgres server
      // are reclassified as standard since we cannot guarantee that ctid will be possible.
      reclassifyCategorisedCtidStreams(streamsCategorised, streamsUnderVacuum.failed());

      List<ConfiguredAirbyteStream> finalListOfStreamsToBeSyncedViaCtid =
          filterStreamsUnderVacuumForCtidSync(streamsUnderVacuum.result(), streamsCategorised.ctidStreams());
      final FileNodeHandler fileNodeHandler =
          PostgresQueryUtils.fileNodeForStreams(database,
              finalListOfStreamsToBeSyncedViaCtid,
              getQuoteString());

      // Streams we failed to query for fileNode - such as in the case of Views are reclassified as
      // standard
      if (!fileNodeHandler.getFailedToQuery().isEmpty()) {
        reclassifyCategorisedCtidStreams(streamsCategorised, fileNodeHandler.getFailedToQuery());
        finalListOfStreamsToBeSyncedViaCtid =
            filterStreamsUnderVacuumForCtidSync(streamsUnderVacuum.result(), streamsCategorised.ctidStreams());
      }
      final CtidStateManager ctidStateManager =
          new CtidPerStreamStateManager(streamsCategorised.ctidStreams().statesFromCtidSync(), fileNodeHandler);
      final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, TableBlockSize> tableBlockSizes =
          PostgresQueryUtils.getTableBlockSizeForStreams(
              database,
              finalListOfStreamsToBeSyncedViaCtid,
              getQuoteString());
      if (finalListOfStreamsToBeSyncedViaCtid.isEmpty()) {
        LOGGER.info("No Streams will be synced via ctid.");
      } else {
        LOGGER.info("Streams to be synced via ctid : {}", finalListOfStreamsToBeSyncedViaCtid.size());
        LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(finalListOfStreamsToBeSyncedViaCtid));
      }

      if (!streamsCategorised.remainingStreams().streamsForCursorBasedSync().isEmpty()) {
        LOGGER.info("Streams to be synced via cursor : {}", streamsCategorised.remainingStreams().streamsForCursorBasedSync().size());
        LOGGER.info("Streams: {}", prettyPrintConfiguredAirbyteStreamList(streamsCategorised.remainingStreams().streamsForCursorBasedSync()));
      } else {
        LOGGER.info("No streams to be synced via cursor");
      }

      final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, CursorBasedStatus> cursorBasedStatusMap =
          getCursorBasedSyncStatusForStreams(database, finalListOfStreamsToBeSyncedViaCtid, postgresCursorBasedStateManager, getQuoteString());

      final PostgresCtidHandler cursorBasedCtidHandler =
          new PostgresCtidHandler(sourceConfig,
              database,
              new CtidPostgresSourceOperations(Optional.empty()),
              getQuoteString(),
              fileNodeHandler,
              tableBlockSizes,
              ctidStateManager,
              namespacePair -> Jsons.jsonNode(cursorBasedStatusMap.get(namespacePair)));

      final List<AutoCloseableIterator<AirbyteMessage>> initialSyncCtidIterators = new ArrayList<>(
          cursorBasedCtidHandler.getInitialSyncCtidIterator(new ConfiguredAirbyteCatalog().withStreams(finalListOfStreamsToBeSyncedViaCtid),
              tableNameToTable,
              emittedAt));
      final List<AutoCloseableIterator<AirbyteMessage>> cursorBasedIterators = new ArrayList<>(super.getIncrementalIterators(database,
          new ConfiguredAirbyteCatalog().withStreams(
              streamsCategorised.remainingStreams()
                  .streamsForCursorBasedSync()),
          tableNameToTable,
          postgresCursorBasedStateManager, emittedAt));

      return Stream
          .of(initialSyncCtidIterators, cursorBasedIterators)
          .flatMap(Collection::stream)
          .collect(Collectors.toList());
    }

    return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
  }

  @Override
  public Set<JdbcPrivilegeDto> getPrivilegesTableForCurrentUser(final JdbcDatabase database,
                                                                final String schema)
      throws SQLException {
    final CheckedFunction<Connection, PreparedStatement, SQLException> statementCreator = connection -> {
      final PreparedStatement ps = connection.prepareStatement(
          """
                 SELECT nspname as table_schema,
                        relname as table_name
                 FROM   pg_class c
                 JOIN   pg_namespace n on c.relnamespace = n.oid
                 WHERE  has_table_privilege(c.oid, 'SELECT')
                 AND    has_schema_privilege(current_user, nspname, 'USAGE')
                 -- r = ordinary table, i = index, S = sequence, t = TOAST table, v = view, m = materialized view, c = composite type, f = foreign table, p = partitioned table, I = partitioned index
                 AND    relkind in ('r', 'm', 'v', 't', 'f', 'p')
                 and    ((? is null) OR nspname = ?)
          """);
      ps.setString(1, schema);
      ps.setString(2, schema);
      return ps;
    };

    return database.queryJsons(statementCreator, sourceOperations::rowToJson)
        .stream()
        .map(e -> JdbcPrivilegeDto.builder()
            .schemaName(e.get("table_schema").asText())
            .tableName(e.get("table_name").asText())
            .build())
        .collect(toSet());
  }

  @VisibleForTesting
  static String getUsername(final JsonNode databaseConfig) {
    final String jdbcUrl = databaseConfig.get(JdbcUtils.JDBC_URL_KEY).asText();
    final String username = databaseConfig.get(JdbcUtils.USERNAME_KEY).asText();

    // Azure Postgres server has this username pattern: <username>@<host>.
    // Inside Postgres, the true username is just <username>.
    // The jdbc_url is constructed in the toDatabaseConfig method.
    if (username.contains("@") && jdbcUrl.contains("azure.com:")) {
      final String[] tokens = username.split("@");
      final String postgresUsername = tokens[0];
      LOGGER.info("Azure username \"{}\" is detected; use \"{}\" to check permission", username, postgresUsername);
      return postgresUsername;
    }

    return username;
  }

  @Override
  protected boolean isNotInternalSchema(final JsonNode jsonNode, final Set<String> internalSchemas) {
    return false;
  }

  @Override
  protected AirbyteStateType getSupportedStateType(final JsonNode config) {
    if (!featureFlags.useStreamCapableState()) {
      return AirbyteStateType.LEGACY;
    }
    return PostgresUtils.isCdc(config) ? AirbyteStateType.GLOBAL : AirbyteStateType.STREAM;
  }

  @Override
  protected int getStateEmissionFrequency() {
    return this.stateEmissionFrequency;
  }

  @VisibleForTesting
  protected void setStateEmissionFrequencyForDebug(final int stateEmissionFrequency) {
    this.stateEmissionFrequency = stateEmissionFrequency;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = PostgresSource.sshWrappedSource();
    LOGGER.info("starting source: {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSource.class);
  }

  @Override
  @Trace(operationName = CHECK_TRACE_OPERATION_NAME)
  public AirbyteConnectionStatus check(final JsonNode config) throws Exception {
    if (PostgresUtils.isCdc(config)) {
      if (config.has(SSL_MODE) && config.get(SSL_MODE).has(MODE)) {
        final String sslModeValue = config.get(SSL_MODE).get(MODE).asText();
        if (INVALID_CDC_SSL_MODES.contains(sslModeValue)) {
          return new AirbyteConnectionStatus()
              .withStatus(Status.FAILED)
              .withMessage(String.format(
                  "In CDC replication mode ssl value '%s' is invalid. Please use one of the following SSL modes: disable, require, verify-ca, verify-full",
                  sslModeValue));
        }
      }
    }
    return super.check(config);
  }

  protected String toSslJdbcParam(final SslMode sslMode) {
    return toSslJdbcParamInternal(sslMode);
  }

  public static String toSslJdbcParamInternal(final SslMode sslMode) {
    final var result = switch (sslMode) {
      case DISABLED -> org.postgresql.jdbc.SslMode.DISABLE.value;
      case ALLOWED -> org.postgresql.jdbc.SslMode.ALLOW.value;
      case PREFERRED -> org.postgresql.jdbc.SslMode.PREFER.value;
      case REQUIRED -> org.postgresql.jdbc.SslMode.REQUIRE.value;
      case VERIFY_CA -> org.postgresql.jdbc.SslMode.VERIFY_CA.value;
      case VERIFY_IDENTITY -> org.postgresql.jdbc.SslMode.VERIFY_FULL.value;
      default -> throw new IllegalArgumentException("unexpected ssl mode");
    };
    LOGGER.info("{} toSslJdbcParam {}", sslMode.name(), result);
    return result;
  }

  @Override
  protected boolean verifyCursorColumnValues(final JdbcDatabase database, final String schema, final String tableName, final String columnName)
      throws SQLException {
    final String query;
    final String resultColName = "nullValue";
    // Query: Only if cursor column allows null values, query whether it contains one
    if (StringUtils.isNotBlank(schema)) {
      query = String.format(NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY,
          schema, tableName, columnName, schema, tableName, columnName, resultColName);
    } else {
      query = String.format(NULL_CURSOR_VALUE_NO_SCHEMA_QUERY,
          tableName, columnName, tableName, columnName, resultColName);
    }
    LOGGER.debug("null value query: {}", query);
    final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(query),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
    Preconditions.checkState(jsonNodes.size() == 1);
    final boolean nullValExist = jsonNodes.get(0).get(resultColName.toLowerCase()).booleanValue(); // For some reason value in node is lowercase
    LOGGER.debug("null value exist: {}", nullValExist);
    return !nullValExist;
  }

  @Override
  protected void estimateFullRefreshSyncSize(final JdbcDatabase database,
                                             final ConfiguredAirbyteStream configuredAirbyteStream) {
    try {
      final String schemaName = configuredAirbyteStream.getStream().getNamespace();
      final String tableName = configuredAirbyteStream.getStream().getName();
      final String fullTableName =
          getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString());

      final List<JsonNode> tableEstimateResult = getFullTableEstimate(database, fullTableName, schemaName, tableName);

      if (!tableEstimateResult.isEmpty() && tableEstimateResult.get(0).has(ROW_COUNT_RESULT_COL) &&
          tableEstimateResult.get(0).has(TOTAL_BYTES_RESULT_COL)) {
        final long syncRowCount = tableEstimateResult.get(0).get(ROW_COUNT_RESULT_COL).asLong();
        final long syncByteCount = tableEstimateResult.get(0).get(TOTAL_BYTES_RESULT_COL).asLong();

        // The fast count query can return negative or otherwise invalid results for small tables. In this
        // case, we can skip emitting an
        // estimate trace altogether since the sync will likely complete quickly.
        if (syncRowCount <= 0) {
          return;
        }

        // Here, we double the bytes estimate to account for serialization. Perhaps a better way to do this
        // is to
        // read a row and Stringify it to better understand the accurate volume of data sent over the wire.
        // However, this approach doesn't account for different row sizes.
        AirbyteTraceMessageUtility.emitEstimateTrace(PLATFORM_DATA_INCREASE_FACTOR * syncByteCount, Type.STREAM, syncRowCount, tableName, schemaName);
        LOGGER.info(String.format("Estimate for table: %s : {sync_row_count: %s, sync_bytes: %s, total_table_row_count: %s, total_table_bytes: %s}",
            fullTableName, syncRowCount, syncByteCount, syncRowCount, syncByteCount));
      }
    } catch (final SQLException e) {
      LOGGER.warn("Error occurred while attempting to estimate sync size", e);
    }
  }

  private List<JsonNode> getFullTableEstimate(final JdbcDatabase database,
                                              final String fullTableName,
                                              final String schemaName,
                                              final String tableName)
      throws SQLException {
    // Construct the table estimate query.
    final String tableEstimateQuery =
        String.format(TABLE_ESTIMATE_QUERY, schemaName, tableName, ROW_COUNT_RESULT_COL, fullTableName, TOTAL_BYTES_RESULT_COL);
    LOGGER.debug("table estimate query: {}", tableEstimateQuery);
    final List<JsonNode> jsonNodes = database.bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(tableEstimateQuery),
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));
    Preconditions.checkState(jsonNodes.size() == 1);
    return jsonNodes;
  }

}
