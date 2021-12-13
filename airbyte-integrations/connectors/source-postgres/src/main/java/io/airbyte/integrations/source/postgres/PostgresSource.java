/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static java.util.stream.Collectors.toList;
import static java.util.stream.Collectors.toSet;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.PostgresJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.dto.JdbcPrivilegeDto;
import io.airbyte.integrations.source.relationaldb.StateManager;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.SyncMode;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSource.class);
  public static final String CDC_LSN = "_ab_cdc_lsn";

  static final String DRIVER_CLASS = "org.postgresql.Driver";

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new PostgresSource(), List.of("host"), List.of("port"));
  }

  PostgresSource() {
    super(DRIVER_CLASS, new PostgresJdbcStreamingQueryConfiguration(), new PostgresSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode config) {
    return toDatabaseConfigStatic(config);
  }

  // todo (cgardens) - restructure AbstractJdbcSource so to take this function in the constructor. the
  // current structure forces us to declarehave a bunch of pure function methods as instance members
  // when they could be static.
  public JsonNode toDatabaseConfigStatic(final JsonNode config) {
    final List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:postgresql://%s:%s/%s?",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    // assume ssl if not explicitly mentioned.
    if (!config.has("ssl") || config.get("ssl").asBoolean()) {
      additionalParameters.add("ssl=true");
      additionalParameters.add("sslmode=require");
    }

    additionalParameters.forEach(x -> jdbcUrl.append(x).append("&"));

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbcUrl.toString());

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
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

    if (isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(PostgresSource::removeIncrementalWithoutPk)
          .map(PostgresSource::setIncrementalToSourceDefined)
          .map(PostgresSource::addCdcMetadataColumns)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config) throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(super.getCheckOperations(config));

    if (isCdc(config)) {
      checkOperations.add(database -> {
        final List<JsonNode> matchingSlots = database.query(connection -> {
          final String sql = "SELECT * FROM pg_replication_slots WHERE slot_name = ? AND plugin = ? AND database = ?";
          final PreparedStatement ps = connection.prepareStatement(sql);
          ps.setString(1, config.get("replication_method").get("replication_slot").asText());
          ps.setString(2, PostgresUtils.getPluginValue(config.get("replication_method")));
          ps.setString(3, config.get("database").asText());

          LOGGER.info("Attempting to find the named replication slot using the query: " + ps.toString());

          return ps;
        }, sourceOperations::rowToJson).collect(toList());

        if (matchingSlots.size() != 1) {
          throw new RuntimeException("Expected exactly one replication slot but found " + matchingSlots.size()
              + ". Please read the docs and add a replication slot to your database.");
        }

      });

      checkOperations.add(database -> {
        final List<JsonNode> matchingPublications = database.query(connection -> {
          final PreparedStatement ps = connection.prepareStatement("SELECT * FROM pg_publication WHERE pubname = ?");
          ps.setString(1, config.get("replication_method").get("publication").asText());

          LOGGER.info("Attempting to find the publication using the query: " + ps.toString());

          return ps;
        }, sourceOperations::rowToJson).collect(toList());

        if (matchingPublications.size() != 1) {
          throw new RuntimeException("Expected exactly one publication but found " + matchingPublications.size()
              + ". Please read the docs and add a publication to your database.");
        }

      });
    }

    return checkOperations;
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode config, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    // this check is used to ensure that have the pgoutput slot available so Debezium won't attempt to
    // create it.
    final AirbyteConnectionStatus check = check(config);

    if (check.getStatus().equals(AirbyteConnectionStatus.Status.FAILED)) {
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
    /**
     * If a customer sets up a postgres source with cdc parameters (replication_slot and publication)
     * but selects all the tables in FULL_REFRESH mode then we would still end up going through this
     * path. We do have a check in place for debezium to make sure only tales in INCREMENTAL mode are
     * synced {@link DebeziumRecordPublisher#getTableWhitelist(ConfiguredAirbyteCatalog)} but we should
     * have a check here as well to make sure that if no table is in INCREMENTAL mode then skip this
     * part
     */
    final JsonNode sourceConfig = database.getSourceConfig();
    if (isCdc(sourceConfig)) {
      final AirbyteDebeziumHandler handler = new AirbyteDebeziumHandler(sourceConfig, PostgresCdcTargetPosition.targetPosition(database),
          PostgresCdcProperties.getDebeziumProperties(sourceConfig), catalog, false);
      return handler.getIncrementalIterators(new PostgresCdcSavedInfoFetcher(stateManager.getCdcStateManager().getCdcState()),
          new PostgresCdcStateHandler(stateManager), new PostgresCdcConnectorMetadataInjector(), emittedAt);

    } else {
      return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
    }
  }

  @VisibleForTesting
  static boolean isCdc(final JsonNode config) {
    final boolean isCdc = config.hasNonNull("replication_method")
        && config.get("replication_method").hasNonNull("replication_slot")
        && config.get("replication_method").hasNonNull("publication");
    LOGGER.info("using CDC: {}", isCdc);
    return isCdc;
  }

  /*
   * It isn't possible to recreate the state of the original database unless we include extra
   * information (like an oid) when using logical replication. By limiting to Full Refresh when we
   * don't have a primary key we dodge the problem for now. As a work around a CDC and non-CDC source
   * could be configured if there's a need to replicate a large non-PK table.
   *
   * Note: in place mutation.
   */
  private static AirbyteStream removeIncrementalWithoutPk(final AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      stream.getSupportedSyncModes().remove(SyncMode.INCREMENTAL);
    }

    return stream;
  }

  @Override
  public Set<JdbcPrivilegeDto> getPrivilegesTableForCurrentUser(final JdbcDatabase database, final String schema) throws SQLException {
    return database.query(connection -> {
      final PreparedStatement ps = connection.prepareStatement(
          "SELECT DISTINCT table_catalog, table_schema, table_name, privilege_type\n"
              + "FROM   information_schema.table_privileges\n"
              + "WHERE  grantee = ? AND privilege_type = 'SELECT'");
      ps.setString(1, database.getDatabaseConfig().get("username").asText());
      return ps;
    }, sourceOperations::rowToJson)
        .collect(toSet())
        .stream()
        .map(e -> JdbcPrivilegeDto.builder()
            .schemaName(e.get("table_schema").asText())
            .tableName(e.get("table_name").asText())
            .build())
        .collect(toSet());
  }

  /*
   * Set all streams that do have incremental to sourceDefined, so that the user cannot set or
   * override a cursor field.
   *
   * Note: in place mutation.
   */
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

    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    properties.set(CDC_LSN, numberType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);

    return stream;
  }

  public static void main(final String[] args) throws Exception {
    final Source source = PostgresSource.sshWrappedSource();
    LOGGER.info("starting source: {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSource.class);
  }

}
