/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

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
import io.airbyte.db.jdbc.JdbcSourceOperations;
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
import java.sql.JDBCType;
import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MySqlSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlSource.class);

  public static final String DRIVER_CLASS = "com.mysql.cj.jdbc.Driver";
  public static final String MYSQL_CDC_OFFSET = "mysql_cdc_offset";
  public static final String MYSQL_DB_HISTORY = "mysql_db_history";
  public static final String CDC_LOG_FILE = "_ab_cdc_log_file";
  public static final String CDC_LOG_POS = "_ab_cdc_log_pos";
  public static final List<String> SSL_PARAMETERS = List.of(
      "useSSL=true",
      "requireSSL=true",
      "verifyServerCertificate=false");

  public static Source sshWrappedSource() {
    return new SshWrappedSource(new MySqlSource(), List.of("host"), List.of("port"));
  }

  public MySqlSource() {
    super(DRIVER_CLASS, new MySqlJdbcStreamingQueryConfiguration(), new MySqlSourceOperations());
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
      checkOperations.add(database -> {
        final List<String> log = database.resultSetQuery(connection -> {
          final String sql = "show variables where Variable_name = 'log_bin'";

          return connection.createStatement().executeQuery(sql);
        }, resultSet -> resultSet.getString("Value")).collect(toList());

        if (log.size() != 1) {
          throw new RuntimeException("Could not query the variable log_bin");
        }

        final String logBin = log.get(0);
        if (!logBin.equalsIgnoreCase("ON")) {
          throw new RuntimeException("The variable log_bin should be set to ON, but it is : " + logBin);
        }
      });

      checkOperations.add(database -> {
        final List<String> format = database.resultSetQuery(connection -> {
          final String sql = "show variables where Variable_name = 'binlog_format'";

          return connection.createStatement().executeQuery(sql);
        }, resultSet -> resultSet.getString("Value")).collect(toList());

        if (format.size() != 1) {
          throw new RuntimeException("Could not query the variable binlog_format");
        }

        final String binlogFormat = format.get(0);
        if (!binlogFormat.equalsIgnoreCase("ROW")) {
          throw new RuntimeException("The variable binlog_format should be set to ROW, but it is : " + binlogFormat);
        }
      });
    }

    checkOperations.add(database -> {
      final List<String> image = database.resultSetQuery(connection -> {
        final String sql = "show variables where Variable_name = 'binlog_row_image'";

        return connection.createStatement().executeQuery(sql);
      }, resultSet -> resultSet.getString("Value")).collect(toList());

      if (image.size() != 1) {
        throw new RuntimeException("Could not query the variable binlog_row_image");
      }

      final String binlogRowImage = image.get(0);
      if (!binlogRowImage.equalsIgnoreCase("FULL")) {
        throw new RuntimeException("The variable binlog_row_image should be set to FULL, but it is : " + binlogRowImage);
      }
    });

    return checkOperations;
  }

  @Override
  public AirbyteCatalog discover(final JsonNode config) throws Exception {
    final AirbyteCatalog catalog = super.discover(config);

    if (isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
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
    final StringBuilder jdbcUrl = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));

    // see MySqlJdbcStreamingQueryConfiguration for more context on why useCursorFetch=true is needed.
    jdbcUrl.append("?useCursorFetch=true");
    jdbcUrl.append("&zeroDateTimeBehavior=convertToNull");
    if (config.get("jdbc_url_params") != null && !config.get("jdbc_url_params").asText().isEmpty()) {
      jdbcUrl.append("&").append(config.get("jdbc_url_params").asText());
    }

    // assume ssl if not explicitly mentioned.
    if (!config.has("ssl") || config.get("ssl").asBoolean()) {
      jdbcUrl.append("&").append(String.join("&", SSL_PARAMETERS));
    }

    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbcUrl.toString());

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
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

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final JdbcDatabase database,
                                                                             final ConfiguredAirbyteCatalog catalog,
                                                                             final Map<String, TableInfo<CommonField<JDBCType>>> tableNameToTable,
                                                                             final StateManager stateManager,
                                                                             final Instant emittedAt) {
    final JsonNode sourceConfig = database.getSourceConfig();
    if (isCdc(sourceConfig) && shouldUseCDC(catalog)) {
      final AirbyteDebeziumHandler handler =
          new AirbyteDebeziumHandler(sourceConfig, MySqlCdcTargetPosition.targetPosition(database), MySqlCdcProperties.getDebeziumProperties(),
              catalog, true);

      return handler.getIncrementalIterators(new MySqlCdcSavedInfoFetcher(stateManager.getCdcStateManager().getCdcState()),
          new MySqlCdcStateHandler(stateManager), new MySqlCdcConnectorMetadataInjector(), emittedAt);
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

  @Override
  protected JdbcSourceOperations getSourceOperations() {
    return new MySqlSourceOperations();
  }

}
