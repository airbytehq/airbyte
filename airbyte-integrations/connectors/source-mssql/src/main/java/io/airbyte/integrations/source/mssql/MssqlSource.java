/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_DELETED_AT;
import static io.airbyte.integrations.debezium.internals.DebeziumEventUtils.CDC_UPDATED_AT;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshWrappedSource;
import io.airbyte.integrations.debezium.AirbyteDebeziumHandler;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.relationaldb.StateManager;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.io.File;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSource extends AbstractJdbcSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSource.class);

  static final String DRIVER_CLASS = "com.microsoft.sqlserver.jdbc.SQLServerDriver";
  public static final String MSSQL_CDC_OFFSET = "mssql_cdc_offset";
  public static final String MSSQL_DB_HISTORY = "mssql_db_history";
  public static final String CDC_LSN = "_ab_cdc_lsn";
  public static final List<String> HOST_KEY = List.of("host");
  public static final List<String> PORT_KEY = List.of("port");

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new MssqlSource(), HOST_KEY, PORT_KEY);
  }

  MssqlSource() {
    super(DRIVER_CLASS, new MssqlJdbcStreamingQueryConfiguration(), new MssqlSourceOperations());
  }

  @Override
  public JsonNode toDatabaseConfig(final JsonNode mssqlConfig) {
    final List<String> additionalParameters = new ArrayList<>();

    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:sqlserver://%s:%s;databaseName=%s;",
        mssqlConfig.get("host").asText(),
        mssqlConfig.get("port").asText(),
        mssqlConfig.get("database").asText()));

    if (mssqlConfig.has("ssl_method")) {
      readSsl(mssqlConfig, additionalParameters);
    }

    if (!additionalParameters.isEmpty()) {
      jdbcUrl.append(String.join(";", additionalParameters));
    }

    return Jsons.jsonNode(ImmutableMap.builder()
        .put("username", mssqlConfig.get("username").asText())
        .put("password", mssqlConfig.get("password").asText())
        .put("jdbc_url", jdbcUrl.toString())
        .build());
  }

  @Override
  public Set<String> getExcludedInternalNameSpaces() {
    return Set.of(
        "INFORMATION_SCHEMA",
        "sys",
        "spt_fallback_db",
        "spt_monitor",
        "spt_values",
        "spt_fallback_usg",
        "MSreplication_options",
        "spt_fallback_dev",
        "cdc"); // is this actually ok? what if the user wants cdc schema for some reason?
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    final AirbyteCatalog catalog = super.discover(config);

    if (isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(MssqlSource::removeIncrementalWithoutPk)
          .map(MssqlSource::setIncrementalToSourceDefined)
          .map(MssqlSource::addCdcMetadataColumns)
          .collect(toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(final JsonNode config) throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(super.getCheckOperations(config));

    if (isCdc(config)) {
      checkOperations.add(database -> assertCdcEnabledInDb(config, database));
      checkOperations.add(database -> assertCdcSchemaQueryable(config, database));
      checkOperations.add(database -> assertSqlServerAgentRunning(database));
      checkOperations.add(database -> assertSnapshotIsolationAllowed(config, database));
    }

    return checkOperations;
  }

  protected void assertCdcEnabledInDb(final JsonNode config, final JdbcDatabase database) throws SQLException {
    final List<JsonNode> queryResponse = database.query(connection -> {
      final String sql = "SELECT name, is_cdc_enabled FROM sys.databases WHERE name = ?";
      final PreparedStatement ps = connection.prepareStatement(sql);
      ps.setString(1, config.get("database").asText());
      LOGGER.info(String.format("Checking that cdc is enabled on database '%s' using the query: '%s'",
          config.get("database").asText(), sql));
      return ps;
    }, sourceOperations::rowToJson).collect(toList());
    if (queryResponse.size() < 1) {
      throw new RuntimeException(String.format(
          "Couldn't find '%s' in sys.databases table. Please check the spelling and that the user has relevant permissions (see docs).",
          config.get("database").asText()));
    }
    if (!(queryResponse.get(0).get("is_cdc_enabled").asBoolean())) {
      throw new RuntimeException(String.format(
          "Detected that CDC is not enabled for database '%s'. Please check the documentation on how to enable CDC on MS SQL Server.",
          config.get("database").asText()));
    }
  }

  protected void assertCdcSchemaQueryable(final JsonNode config, final JdbcDatabase database) throws SQLException {
    final List<JsonNode> queryResponse = database.query(connection -> {
      final String sql = "USE " + config.get("database").asText() + "; SELECT * FROM cdc.change_tables";
      final PreparedStatement ps = connection.prepareStatement(sql);
      LOGGER.info(String.format("Checking user '%s' can query the cdc schema and that we have at least 1 cdc enabled table using the query: '%s'",
          config.get("username").asText(), sql));
      return ps;
    }, sourceOperations::rowToJson).collect(toList());
    // Ensure at least one available CDC table
    if (queryResponse.size() < 1) {
      throw new RuntimeException("No cdc-enabled tables found. Please check the documentation on how to enable CDC on MS SQL Server.");
    }
  }

  // todo: ensure this works for Azure managed SQL (since it uses different sql server agent)
  protected void assertSqlServerAgentRunning(final JdbcDatabase database) throws SQLException {
    try {
      final List<JsonNode> queryResponse = database.query(connection -> {
        final String sql = "SELECT status_desc FROM sys.dm_server_services WHERE [servicename] LIKE 'SQL Server Agent%'";
        final PreparedStatement ps = connection.prepareStatement(sql);
        LOGGER.info(String.format("Checking that the SQL Server Agent is running using the query: '%s'", sql));
        return ps;
      }, sourceOperations::rowToJson).collect(toList());
      if (!(queryResponse.get(0).get("status_desc").toString().contains("Running"))) {
        throw new RuntimeException(String.format(
            "The SQL Server Agent is not running. Current state: '%s'. Please check the documentation on ensuring SQL Server Agent is running.",
            queryResponse.get(0).get("status_desc").toString()));
      }
    } catch (final Exception e) {
      if (e.getCause() != null && e.getCause().getClass().equals(com.microsoft.sqlserver.jdbc.SQLServerException.class)) {
        LOGGER.warn(String.format("Skipping check for whether the SQL Server Agent is running, SQLServerException thrown: '%s'",
            e.getMessage()));
      } else {
        throw e;
      }
    }
  }

  protected void assertSnapshotIsolationAllowed(final JsonNode config, final JdbcDatabase database) throws SQLException {
    final List<JsonNode> queryResponse = database.query(connection -> {
      final String sql = "SELECT name, snapshot_isolation_state FROM sys.databases WHERE name = ?";
      final PreparedStatement ps = connection.prepareStatement(sql);
      ps.setString(1, config.get("database").asText());
      LOGGER.info(String.format("Checking that snapshot isolation is enabled on database '%s' using the query: '%s'",
          config.get("database").asText(), sql));
      return ps;
    }, sourceOperations::rowToJson).collect(toList());
    if (queryResponse.size() < 1) {
      throw new RuntimeException(String.format(
          "Couldn't find '%s' in sys.databases table. Please check the spelling and that the user has relevant permissions (see docs).",
          config.get("database").asText()));
    }
    if (queryResponse.get(0).get("snapshot_isolation_state").asInt() != 1) {
      throw new RuntimeException(String.format(
          "Detected that snapshot isolation is not enabled for database '%s'. MSSQL CDC relies on snapshot isolation. "
              + "Please check the documentation on how to enable snapshot isolation on MS SQL Server.",
          config.get("database").asText()));
    }
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (isCdc(sourceConfig) && shouldUseCDC(catalog)) {
      LOGGER.info("using CDC: {}", true);
      final AirbyteDebeziumHandler handler = new AirbyteDebeziumHandler(sourceConfig,
          MssqlCdcTargetPosition.getTargetPosition(database, sourceConfig.get("database").asText()),
          MssqlCdcProperties.getDebeziumProperties(), catalog, true);
      return handler.getIncrementalIterators(new MssqlCdcSavedInfoFetcher(stateManager.getCdcStateManager().getCdcState()),
          new MssqlCdcStateHandler(stateManager), new MssqlCdcConnectorMetadataInjector(), emittedAt);
    } else {
      LOGGER.info("using CDC: {}", false);
      return super.getIncrementalIterators(database, catalog, tableNameToTable, stateManager, emittedAt);
    }
  }

  private static boolean isCdc(final JsonNode config) {
    return config.hasNonNull("replication_method")
        && ReplicationMethod.valueOf(config.get("replication_method").asText())
            .equals(ReplicationMethod.CDC);
  }

  private static boolean shouldUseCDC(final ConfiguredAirbyteCatalog catalog) {
    final Optional<SyncMode> any = catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode)
        .filter(syncMode -> syncMode == SyncMode.INCREMENTAL).findAny();
    return any.isPresent();
  }

  // Note: in place mutation.
  private static AirbyteStream removeIncrementalWithoutPk(final AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      stream.getSupportedSyncModes().remove(SyncMode.INCREMENTAL);
    }

    return stream;
  }

  // Note: in place mutation.
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
    properties.set(CDC_LSN, stringType);
    properties.set(CDC_UPDATED_AT, stringType);
    properties.set(CDC_DELETED_AT, stringType);

    return stream;
  }

  private void readSsl(final JsonNode sslMethod, final List<String> additionalParameters) {
    final JsonNode config = sslMethod.get("ssl_method");
    switch (config.get("ssl_method").asText()) {
      case "unencrypted" -> additionalParameters.add("encrypt=false");
      case "encrypted_trust_server_certificate" -> {
        additionalParameters.add("encrypt=true");
        additionalParameters.add("trustServerCertificate=true");
      }
      case "encrypted_verify_certificate" -> {
        additionalParameters.add("encrypt=true");

        // trust store location code found at https://stackoverflow.com/a/56570588
        final String trustStoreLocation = Optional.ofNullable(System.getProperty("javax.net.ssl.trustStore"))
            .orElseGet(() -> System.getProperty("java.home") + "/lib/security/cacerts");
        final File trustStoreFile = new File(trustStoreLocation);
        if (!trustStoreFile.exists()) {
          throw new RuntimeException(
              "Unable to locate the Java TrustStore: the system property javax.net.ssl.trustStore is undefined or "
                  + trustStoreLocation + " does not exist.");
        }
        final String trustStorePassword = System.getProperty("javax.net.ssl.trustStorePassword");
        additionalParameters.add("trustStore=" + trustStoreLocation);
        if (trustStorePassword != null && !trustStorePassword.isEmpty()) {
          additionalParameters.add("trustStorePassword=" + config.get("trustStorePassword").asText());
        }
        if (config.has("hostNameInCertificate")) {
          additionalParameters.add("hostNameInCertificate=" + config.get("hostNameInCertificate").asText());
        }
      }
    }
  }

  public static void main(final String[] args) throws Exception {
    final Source source = MssqlSource.sshWrappedSource();
    LOGGER.info("starting source: {}", MssqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MssqlSource.class);
  }

  public enum ReplicationMethod {
    STANDARD,
    CDC
  }

}
