/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.db.jdbc.JdbcUtils.AMPERSAND;
import static io.airbyte.db.jdbc.JdbcUtils.EQUALS;
import static io.airbyte.db.jdbc.JdbcUtils.PLATFORM_DATA_INCREASE_FACTOR;
import static io.airbyte.integrations.debezium.AirbyteDebeziumHandler.shouldUseCDC;
import static io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils.PARAM_CA_CERTIFICATE;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.NULL_CURSOR_VALUE_NO_SCHEMA_QUERY;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.NULL_CURSOR_VALUE_WITH_SCHEMA_QUERY;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.ROW_COUNT_RESULT_COL;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.TABLE_ESTIMATE_QUERY;
import static io.airbyte.integrations.source.postgres.PostgresQueryUtils.TOTAL_BYTES_RESULT_COL;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getFullyQualifiedTableNameWithQuoting;
import static io.airbyte.integrations.source.relationaldb.RelationalDbQueryUtils.getIdentifierWithQuoting;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.DISABLE;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.PARAM_SSL_MODE;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.streaming.AdaptiveStreamingQueryConfig;
import io.airbyte.integrations.base.AirbyteTraceMessageUtility;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.debezium.internals.PostgresDebeziumStateUtil;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.JdbcSSLConnectionUtils;
import io.airbyte.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.integrations.source.relationaldb.CursorInfo;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteEstimateTraceMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.OptionalLong;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSource extends AbstractJdbcSource<PostgresType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSource.class);
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  public static final String PARAM_SSLMODE = "sslmode";
  public static final String SSL_MODE = "ssl_mode";
  public static final String PARAM_SSL = "ssl";
  public static final String PARAM_SSL_TRUE = "true";
  public static final String PARAM_SSL_FALSE = "false";
  public static final String SSL_ROOT_CERT = "sslrootcert";

  static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();
  public static final String CA_CERTIFICATE_PATH = "ca_certificate_path";
  public static final String SSL_KEY = "sslkey";
  public static final String SSL_PASSWORD = "sslpassword";
  public static final String MODE = "mode";

  private List<String> schemas;
  private final FeatureFlags featureFlags;
  private static final Set<String> INVALID_CDC_SSL_MODES = ImmutableSet.of("allow", "prefer");

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new PostgresSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  PostgresSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new PostgresSourceOperations());
    this.featureFlags = new EnvVariableFeatureFlags();
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    return Collections.emptyMap();
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final List<String> additionalParameters = new ArrayList<>();

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
    LOGGER.debug("jdbc url: {}", jdbcUrl.toString());
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    configBuilder.putAll(sslParameters);

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public String toJDBCQueryParams(final Map<String, String> sslParams) {
    return Objects.isNull(sslParams) ? ""
        : sslParams.entrySet()
            .stream()
            .map((entry) -> {
              try {
                final String result = switch (entry.getKey()) {
                  case AbstractJdbcSource.SSL_MODE -> PARAM_SSLMODE + EQUALS + toSslJdbcParam(SslMode.valueOf(entry.getValue()))
                      + JdbcUtils.AMPERSAND + PARAM_SSL + EQUALS + (entry.getValue() == DISABLE ? PARAM_SSL_FALSE : PARAM_SSL_TRUE);
                  case CA_CERTIFICATE_PATH -> SSL_ROOT_CERT + EQUALS + entry.getValue();
                  case CLIENT_KEY_STORE_URL -> SSL_KEY + EQUALS + Path.of(new URI(entry.getValue()));
                  case CLIENT_KEY_STORE_PASS -> SSL_PASSWORD + EQUALS + entry.getValue();
                  default -> "";
                };
                return result;
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
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    final AirbyteCatalog catalog = super.discover(config);

    if (PostgresUtils.isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(PostgresCdcCatalogHelper::overrideSyncModes)
          .map(PostgresCdcCatalogHelper::removeIncrementalWithoutPk)
          .map(PostgresCdcCatalogHelper::setIncrementalToSourceDefined)
          .map(PostgresCdcCatalogHelper::addCdcMetadataColumns)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public List<TableInfo<CommonField<PostgresType>>> discoverInternal(final JdbcDatabase database) throws Exception {
    final List<TableInfo<CommonField<PostgresType>>> rawTables = discoverRawTables(database);
    final Set<AirbyteStreamNameNamespacePair> publicizedTablesInCdc = PostgresCdcCatalogHelper.getPublicizedTables(database);

    if (publicizedTablesInCdc.isEmpty()) {
      return rawTables;
    }
    // under cdc mode, only return tables that are in the publication
    return rawTables.stream()
        .filter(table -> publicizedTablesInCdc.contains(new AirbyteStreamNameNamespacePair(table.getName(), table.getNameSpace())))
        .collect(toList());
  }

  public List<TableInfo<CommonField<PostgresType>>> discoverRawTables(final JdbcDatabase database) throws Exception {
    if (schemas != null && !schemas.isEmpty()) {
      // process explicitly selected (from UI) schemas
      final List<TableInfo<CommonField<PostgresType>>> internals = new ArrayList<>();
      for (final String schema : schemas) {
        LOGGER.info("Checking schema: {}", schema);
        final List<TableInfo<CommonField<PostgresType>>> tables = super.discoverInternal(database, schema);
        internals.addAll(tables);
        for (final TableInfo<CommonField<PostgresType>> table : tables) {
          LOGGER.info("Found table: {}.{}", table.getNameSpace(), table.getName());
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

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config)
      throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(
        super.getCheckOperations(config));

    if (PostgresUtils.isCdc(config)) {
      checkOperations.add(database -> {
        final List<JsonNode> matchingSlots = getReplicationSlot(database, config);

        if (matchingSlots.size() != 1) {
          throw new RuntimeException(
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
          throw new RuntimeException(
              "Expected exactly one publication but found " + matchingPublications.size()
                  + ". Please read the docs and add a publication to your database.");
        }

      });

      checkOperations.add(database -> {
        PostgresUtils.checkFirstRecordWaitTime(config);
      });
    }

    return checkOperations;
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config,
                                                    final ConfiguredAirbyteCatalog catalog,
                                                    final JsonNode state)
      throws Exception {
    // this check is used to ensure that have the pgoutput slot available so Debezium won't attempt to
    // create it.
    final AirbyteConnectionStatus check = check(config);

    if (check.getStatus().equals(Status.FAILED)) {
      throw new RuntimeException("Unable establish a connection: " + check.getMessage());
    }

    return super.read(config, catalog, state);
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<PostgresType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (PostgresUtils.isCdc(sourceConfig) && shouldUseCDC(catalog)) {
      final Duration firstRecordWaitTime = PostgresUtils.getFirstRecordWaitTime(sourceConfig);
      LOGGER.info("First record waiting time: {} seconds", firstRecordWaitTime.getSeconds());

      final PostgresDebeziumStateUtil postgresDebeziumStateUtil = new PostgresDebeziumStateUtil();
      final JsonNode state =
          (stateManager.getCdcStateManager().getCdcState() == null || stateManager.getCdcStateManager().getCdcState().getState() == null) ? null
              : Jsons.clone(stateManager.getCdcStateManager().getCdcState().getState());

      final OptionalLong savedOffset = postgresDebeziumStateUtil.savedOffset(
          Jsons.clone(PostgresCdcProperties.getDebeziumDefaultProperties(database)),
          catalog,
          state,
          sourceConfig);

      final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(
          // We can assume that there will be only 1 replication slot cause before the sync starts for
          // Postgres CDC,
          // we run all the check operations and one of the check validates that the replication slot exists
          // and has only 1 entry
          getReplicationSlot(database, sourceConfig).get(0),
          savedOffset);

      if (!savedOffsetAfterReplicationSlotLSN) {
        LOGGER.warn("Saved offset is before Replication slot's confirmed_flush_lsn, Airbyte will trigger sync from scratch");
      } else if (PostgresUtils.shouldFlushAfterSync(sourceConfig)) {
        postgresDebeziumStateUtil.commitLSNToPostgresDatabase(database.getDatabaseConfig(),
            savedOffset,
            sourceConfig.get("replication_method").get("replication_slot").asText(),
            sourceConfig.get("replication_method").get("publication").asText(),
            PostgresUtils.getPluginValue(sourceConfig.get("replication_method")));
      }

      final AirbyteDebeziumHandler handler = new AirbyteDebeziumHandler(sourceConfig,
          PostgresCdcTargetPosition.targetPosition(database), false, firstRecordWaitTime);
      final PostgresCdcStateHandler postgresCdcStateHandler = new PostgresCdcStateHandler(stateManager);
      final List<ConfiguredAirbyteStream> streamsToSnapshot = identifyStreamsToSnapshot(catalog, stateManager);
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(catalog,
          new PostgresCdcSavedInfoFetcher(savedOffsetAfterReplicationSlotLSN ? stateManager.getCdcStateManager().getCdcState() : null),
          postgresCdcStateHandler,
          new PostgresCdcConnectorMetadataInjector(),
          PostgresCdcProperties.getDebeziumDefaultProperties(database),
          emittedAt);
      if (!savedOffsetAfterReplicationSlotLSN || streamsToSnapshot.isEmpty()) {
        return Collections.singletonList(incrementalIteratorSupplier.get());
      }

      final AutoCloseableIterator<AirbyteMessage> snapshotIterator = handler.getSnapshotIterators(
          new ConfiguredAirbyteCatalog().withStreams(streamsToSnapshot), new PostgresCdcConnectorMetadataInjector(),
          PostgresCdcProperties.getSnapshotProperties(database), postgresCdcStateHandler, emittedAt);
      return Collections.singletonList(
          AutoCloseableIterators.concatWithEagerClose(snapshotIterator, AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier)));

    } else {
      return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
    }
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

  // TODO This is a temporary override so that the Postgres source can take advantage of per-stream
  // state
  @Override
  protected List<AirbyteStateMessage> generateEmptyInitialState(final JsonNode config) {
    if (!featureFlags.useStreamCapableState()) {
      return List.of(new AirbyteStateMessage()
          .withType(AirbyteStateType.LEGACY)
          .withData(Jsons.jsonNode(new DbState())));
    }
    if (getSupportedStateType(config) == AirbyteStateType.GLOBAL) {
      final AirbyteGlobalState globalState = new AirbyteGlobalState()
          .withSharedState(Jsons.jsonNode(new CdcState()))
          .withStreamStates(List.of());
      return List.of(new AirbyteStateMessage().withType(AirbyteStateType.GLOBAL).withGlobal(globalState));
    } else {
      return List.of(new AirbyteStateMessage()
          .withType(AirbyteStateType.STREAM)
          .withStream(new AirbyteStreamState()));
    }
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
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = PostgresSource.sshWrappedSource();
    LOGGER.info("starting source: {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSource.class);
  }

  @Override
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

  @Override
  protected String toSslJdbcParam(final SslMode sslMode) {
    return toSslJdbcParamInternal(sslMode);
  }

  protected static String toSslJdbcParamInternal(final SslMode sslMode) {
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

  @Override
  protected void estimateIncrementalSyncSize(final JdbcDatabase database,
                                             final ConfiguredAirbyteStream configuredAirbyteStream,
                                             final CursorInfo cursorInfo,
                                             final PostgresType cursorFieldType) {
    try {
      final String schemaName = configuredAirbyteStream.getStream().getNamespace();
      final String tableName = configuredAirbyteStream.getStream().getName();
      final String fullTableName =
          getFullyQualifiedTableNameWithQuoting(schemaName, tableName, getQuoteString());

      final List<JsonNode> tableEstimateResult = getFullTableEstimate(database, fullTableName, schemaName, tableName);

      final long tableRowCount = tableEstimateResult.get(0).get(ROW_COUNT_RESULT_COL).asLong();
      final long tableByteCount = tableEstimateResult.get(0).get(TOTAL_BYTES_RESULT_COL).asLong();

      // The fast count query can return negative or otherwise invalid results for small tables. In this
      // case, we can skip emitting an
      // estimate trace altogether since the sync will likely complete quickly.
      if (tableRowCount <= 0) {
        return;
      }

      final long syncRowCount;
      final long syncByteCount;

      syncRowCount = getIncrementalTableRowCount(database, fullTableName, cursorInfo, cursorFieldType);
      syncByteCount = (tableByteCount / tableRowCount) * syncRowCount;

      // Here, we double the bytes estimate to account for serialization. Perhaps a better way to do this
      // is to
      // read a row and Stringify it to better understand the accurate volume of data sent over the wire.
      // However, this approach doesn't account for different row sizes
      AirbyteTraceMessageUtility.emitEstimateTrace(PLATFORM_DATA_INCREASE_FACTOR * syncByteCount, Type.STREAM, syncRowCount, tableName, schemaName);
      LOGGER.info(String.format("Estimate for table: %s : {sync_row_count: %s, sync_bytes: %s, total_table_row_count: %s, total_table_bytes: %s}",
          fullTableName, syncRowCount, syncByteCount, tableRowCount, tableRowCount));
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

  private long getIncrementalTableRowCount(final JdbcDatabase database,
                                           final String fullTableName,
                                           final CursorInfo cursorInfo,
                                           final PostgresType cursorFieldType)
      throws SQLException {
    final String quotedCursorField = getIdentifierWithQuoting(cursorInfo.getCursorField(), getQuoteString());

    // Calculate actual number of rows to sync here.
    final List<JsonNode> result = database.queryJsons(
        connection -> {
          LOGGER.info("Preparing query for table: {}", fullTableName);
          final String operator;
          if (cursorInfo.getCursorRecordCount() <= 0L) {
            operator = ">";
          } else {
            final long actualRecordCount = getActualCursorRecordCount(
                connection, fullTableName, quotedCursorField, cursorFieldType, cursorInfo.getCursor());
            LOGGER.info("Table {} cursor count: expected {}, actual {}", fullTableName, cursorInfo.getCursorRecordCount(), actualRecordCount);
            if (actualRecordCount == cursorInfo.getCursorRecordCount()) {
              operator = ">";
            } else {
              operator = ">=";
            }
          }

          final StringBuilder sql = new StringBuilder(String.format("SELECT COUNT(*) FROM %s WHERE %s %s ?",
              fullTableName,
              quotedCursorField,
              operator));

          final PreparedStatement preparedStatement = connection.prepareStatement(sql.toString());
          LOGGER.info("Executing query for table {}: {}", fullTableName, preparedStatement);
          sourceOperations.setCursorField(preparedStatement, 1, cursorFieldType, cursorInfo.getCursor());
          return preparedStatement;
        },
        resultSet -> JdbcUtils.getDefaultSourceOperations().rowToJson(resultSet));

    Preconditions.checkState(result.size() == 1);
    return result.get(0).get("count").asLong();
  }

}
