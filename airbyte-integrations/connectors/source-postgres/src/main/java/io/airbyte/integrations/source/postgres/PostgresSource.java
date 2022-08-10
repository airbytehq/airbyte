/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.debezium.AirbyteDebeziumHandler.shouldUseCDC;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.DISABLE;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.PARAM_MODE;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.PARAM_SSL;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.PARAM_SSL_MODE;
import static io.airbyte.integrations.util.PostgresSslConnectionUtils.obtainConnectionOptions;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import com.google.common.collect.Sets;
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
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.debezium.internals.PostgresDebeziumStateUtil;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.integrations.source.relationaldb.models.CdcState;
import io.airbyte.integrations.source.relationaldb.models.DbState;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.sql.Connection;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Duration;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSource.class);
  private static final int INTERMEDIATE_STATE_EMISSION_FREQUENCY = 10_000;

  static final String DRIVER_CLASS = DatabaseDriver.POSTGRESQL.getDriverClassName();
  static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      "ssl", "true",
      "sslmode", "require");
  private List<String> schemas;
  private final FeatureFlags featureFlags;

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new PostgresSource(), JdbcUtils.HOST_LIST_KEY, JdbcUtils.PORT_LIST_KEY);
  }

  PostgresSource() {
    super(DRIVER_CLASS, AdaptiveStreamingQueryConfig::new, new PostgresSourceOperations());
    this.featureFlags = new EnvVariableFeatureFlags();
  }

  @Override
  protected Map<String, String> getDefaultConnectionProperties(final JsonNode config) {
    if (JdbcUtils.useSsl(config)) {
      return SSL_JDBC_PARAMETERS;
    } else {
      return Collections.emptyMap();
    }
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    final List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:postgresql://%s:%s/%s?",
        config.get(JdbcUtils.HOST_KEY).asText(),
        config.get(JdbcUtils.PORT_KEY).asText(),
        config.get(JdbcUtils.DATABASE_KEY).asText()));

    if (config.get(JdbcUtils.JDBC_URL_PARAMS_KEY) != null && !config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText().isEmpty()) {
      jdbcUrl.append(config.get(JdbcUtils.JDBC_URL_PARAMS_KEY).asText()).append("&");
    }

    // assume ssl if not explicitly mentioned.
    if (!config.has(PARAM_SSL) || config.get(PARAM_SSL).asBoolean()) {
      if (config.has(PARAM_SSL_MODE)) {
        if (DISABLE.equals(config.get(PARAM_SSL_MODE).get(PARAM_MODE).asText())) {
          additionalParameters.add("sslmode=disable");
        } else {
          final var parametersList = obtainConnectionOptions(config.get(PARAM_SSL_MODE))
              .entrySet()
              .stream()
              .map(e -> e.getKey() + "=" + e.getValue())
              .toList();
          additionalParameters.addAll(parametersList);
        }
      } else {
        additionalParameters.add("ssl=true");
        additionalParameters.add("sslmode=require");
      }
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

    final Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put(JdbcUtils.USERNAME_KEY, config.get(JdbcUtils.USERNAME_KEY).asText())
        .put(JdbcUtils.JDBC_URL_KEY, jdbcUrl.toString());

    if (config.has(JdbcUtils.PASSWORD_KEY)) {
      configBuilder.put(JdbcUtils.PASSWORD_KEY, config.get(JdbcUtils.PASSWORD_KEY).asText());
    }

    return Jsons.jsonNode(configBuilder.build());
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
          .map(PostgresCdcCatalogHelper::removeIncrementalWithoutPk)
          .map(PostgresCdcCatalogHelper::setIncrementalToSourceDefined)
          .map(PostgresCdcCatalogHelper::addCdcMetadataColumns)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public List<TableInfo<CommonField<JDBCType>>> discoverInternal(final JdbcDatabase database) throws Exception {
    final List<TableInfo<CommonField<JDBCType>>> rawTables = discoverRawTables(database);
    final Set<AirbyteStreamNameNamespacePair> publicizedTablesInCdc = PostgresCdcCatalogHelper.getPublicizedTables(database);

    if (publicizedTablesInCdc.isEmpty()) {
      return rawTables;
    }
    // under cdc mode, only return tables that are in the publication
    return rawTables.stream()
        .filter(table -> publicizedTablesInCdc.contains(new AirbyteStreamNameNamespacePair(table.getName(), table.getNameSpace())))
        .collect(toList());
  }

  public List<TableInfo<CommonField<JDBCType>>> discoverRawTables(final JdbcDatabase database) throws Exception {
    if (schemas != null && !schemas.isEmpty()) {
      // process explicitly selected (from UI) schemas
      final List<TableInfo<CommonField<JDBCType>>> internals = new ArrayList<>();
      for (final String schema : schemas) {
        LOGGER.info("Checking schema: {}", schema);
        final List<TableInfo<CommonField<JDBCType>>> tables = super.discoverInternal(database, schema);
        internals.addAll(tables);
        for (final TableInfo<CommonField<JDBCType>> table : tables) {
          LOGGER.info("Found table: {}.{}", table.getNameSpace(), table.getName());
        }
      }
      return internals;
    } else {
      LOGGER.info("No schemas explicitly set on UI to process, so will process all of existing schemas in DB");
      return super.discoverInternal(database);
    }
  }

  private List<JsonNode> getReplicationSlot(final JdbcDatabase database, final JsonNode config) {
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
                                                                             final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
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
      final boolean savedOffsetAfterReplicationSlotLSN = postgresDebeziumStateUtil.isSavedOffsetAfterReplicationSlotLSN(
          Jsons.clone(PostgresCdcProperties.getDebeziumDefaultProperties(sourceConfig)),
          catalog,
          state,
          // We can assume that there will be only 1 replication slot cause before the sync starts for
          // Postgres CDC,
          // we run all the check operations and one of the check validates that the replication slot exists
          // and has only 1 entry
          getReplicationSlot(database, sourceConfig).get(0),
          sourceConfig);

      if (!savedOffsetAfterReplicationSlotLSN) {
        LOGGER.warn("Saved offset is before Replication slot's confirmed_flush_lsn, Airbyte will trigger sync from scratch");
      }

      final AirbyteDebeziumHandler handler = new AirbyteDebeziumHandler(sourceConfig,
          PostgresCdcTargetPosition.targetPosition(database), false, firstRecordWaitTime);
      final PostgresCdcStateHandler postgresCdcStateHandler = new PostgresCdcStateHandler(stateManager);
      final List<ConfiguredAirbyteStream> streamsToSnapshot = identifyStreamsToSnapshot(catalog, stateManager);
      final Supplier<AutoCloseableIterator<AirbyteMessage>> incrementalIteratorSupplier = () -> handler.getIncrementalIterators(catalog,
          new PostgresCdcSavedInfoFetcher(savedOffsetAfterReplicationSlotLSN ? stateManager.getCdcStateManager().getCdcState() : null),
          postgresCdcStateHandler,
          new PostgresCdcConnectorMetadataInjector(),
          PostgresCdcProperties.getDebeziumDefaultProperties(sourceConfig),
          emittedAt);
      if (!savedOffsetAfterReplicationSlotLSN || streamsToSnapshot.isEmpty()) {
        return Collections.singletonList(incrementalIteratorSupplier.get());
      }

      final AutoCloseableIterator<AirbyteMessage> snapshotIterator = handler.getSnapshotIterators(
          new ConfiguredAirbyteCatalog().withStreams(streamsToSnapshot), new PostgresCdcConnectorMetadataInjector(),
          PostgresCdcProperties.getSnapshotProperties(), postgresCdcStateHandler, emittedAt);
      return Collections.singletonList(
          AutoCloseableIterators.concatWithEagerClose(snapshotIterator, AutoCloseableIterators.lazyIterator(incrementalIteratorSupplier)));

    } else {
      return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
    }
  }

  protected List<ConfiguredAirbyteStream> identifyStreamsToSnapshot(final ConfiguredAirbyteCatalog catalog, final StateManager stateManager) {
    final Set<AirbyteStreamNameNamespacePair> alreadySyncedStreams = stateManager.getCdcStateManager().getInitialStreamsSynced();
    if (alreadySyncedStreams.isEmpty() && (stateManager.getCdcStateManager().getCdcState() == null
        || stateManager.getCdcStateManager().getCdcState().getState() == null)) {
      return Collections.emptyList();
    }

    final Set<AirbyteStreamNameNamespacePair> allStreams = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);

    final Set<AirbyteStreamNameNamespacePair> newlyAddedStreams = new HashSet<>(Sets.difference(allStreams, alreadySyncedStreams));

    return catalog.getStreams().stream()
        .filter(stream -> newlyAddedStreams.contains(AirbyteStreamNameNamespacePair.fromAirbyteSteam(stream.getStream())))
        .map(Jsons::clone)
        .collect(Collectors.toList());
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

  protected int getStateEmissionFrequency() {
    return INTERMEDIATE_STATE_EMISSION_FREQUENCY;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = PostgresSource.sshWrappedSource();
    LOGGER.info("starting source: {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSource.class);
  }

}
