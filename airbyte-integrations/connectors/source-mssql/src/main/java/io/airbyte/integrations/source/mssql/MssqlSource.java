/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.integrations.source.mssql.AirbyteFileOffsetBackingStore.initializeState;
import static io.airbyte.integrations.source.mssql.AirbyteSchemaHistoryStorage.initializeDBHistory;
import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.CompositeIterator;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.JdbcStateManager;
import io.airbyte.integrations.source.jdbc.models.CdcState;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import io.debezium.connector.sqlserver.Lsn;
import io.debezium.engine.ChangeEvent;
import java.io.File;
import java.io.IOException;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlSource.class);

  static final String DRIVER_CLASS = "com.microsoft.sqlserver.jdbc.SQLServerDriver";
  public static final String MSSQL_CDC_OFFSET = "mssql_cdc_offset";
  public static final String MSSQL_DB_HISTORY = "mssql_db_history";

  public MssqlSource() {
    super(DRIVER_CLASS, new MssqlJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode mssqlConfig) {
    List<String> additionalParameters = new ArrayList<>();

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
  public Set<String> getExcludedInternalSchemas() {
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
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    AirbyteCatalog catalog = super.discover(config);

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
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(JsonNode config) throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(super.getCheckOperations(config));

    if (isCdc(config)) {

      // note, it's possible these queries could fail if user doesn't have correct permissions
      // hopefully in these cases it should be evident from the SQLServerException thrown

      // check that cdc is enabled on database
      checkOperations.add(database -> {
        List<JsonNode> queryResponse = database.query(connection -> {
          final String sql = "SELECT name, is_cdc_enabled FROM sys.databases WHERE name = ?";
          PreparedStatement ps = connection.prepareStatement(sql);
          ps.setString(1, config.get("database").asText());
          LOGGER.info(String.format("Checking that cdc is enabled on database '%s' using the query: '%s'",
              config.get("database").asText(), sql));
          return ps;
        }, JdbcUtils::rowToJson).collect(toList());

        if (queryResponse.size() < 1) {
          throw new RuntimeException(String.format(
              "Couldn't find '%s' in sys.databases table. Please check the spelling and that the user has relevant permissions (see docs).",
              config.get("database").asText()));
        }

        if ( ! (queryResponse.get(0).get("is_cdc_enabled").asBoolean())) {
          throw new RuntimeException(String.format(
              "Detected that CDC is not enabled for database '%s'. Please check the documentation on how to enable CDC on MS SQL Server.",
              config.get("database").asText()));
        }
      });

      // check that we can query cdc schema and check we have at least 1 table with cdc enabled that this user can see
      checkOperations.add(database -> {
        List<JsonNode> queryResponse = database.query(connection -> {
          final String sql = "SELECT * FROM cdc.change_tables";
          PreparedStatement ps = connection.prepareStatement(sql);
          LOGGER.info(String.format("Checking user '%s' can query the cdc schema and that we have at least 1 cdc enabled table using the query: '%s'",
              config.get("username").asText(), sql));
          return ps;
        }, JdbcUtils::rowToJson).collect(toList());

        if (queryResponse.size() < 1) {
          throw new RuntimeException("No cdc-enabled tables found. Please check the documentation on how to enable CDC on MS SQL Server.");
        }
      });

      // check sql server agent is running
      // todo: ensure this works for Azure managed SQL (since it uses different sql server agent)
      checkOperations.add(database -> {
        try {
          List<JsonNode> queryResponse = database.query(connection -> {
            final String sql = "SELECT status_desc FROM sys.dm_server_services WHERE [servicename] LIKE 'SQL Server Agent%'";
            PreparedStatement ps = connection.prepareStatement(sql);
            LOGGER.info(String.format("Checking that the SQL Server Agent is running using the query: '%s'", sql));
            return ps;
          }, JdbcUtils::rowToJson).collect(toList());

          if ( ! (queryResponse.get(0).get("status_desc").toString().contains("Running"))) {
            throw new RuntimeException(String.format(
                "The SQL Server Agent is not running. Current state: '%s'. Please check the documentation on ensuring SQL Server Agent is running.",
                queryResponse.get(0).get("status_desc").toString()));
          }
        } catch (Exception e) {
          if (e.getCause() != null && e.getCause().getClass().equals(com.microsoft.sqlserver.jdbc.SQLServerException.class)) {
            LOGGER.warn(String.format("Skipping check for whether the SQL Server Agent is running, SQLServerException thrown: '%s'",
                e.getMessage()));
          } else {
            throw e;
          }
        }
      });

      // check that snapshot isolation is allowed
      checkOperations.add(database -> {
        List<JsonNode> queryResponse = database.query(connection -> {
          final String sql = "SELECT name, snapshot_isolation_state FROM sys.databases WHERE name = ?";
          PreparedStatement ps = connection.prepareStatement(sql);
          ps.setString(1, config.get("database").asText());
          LOGGER.info(String.format("Checking that snapshot isolation is enabled on database '%s' using the query: '%s'",
              config.get("database").asText(), sql));
          return ps;
        }, JdbcUtils::rowToJson).collect(toList());

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
      });

    }

    return checkOperations;
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(JsonNode config,
                                                                             JdbcDatabase database,
                                                                             ConfiguredAirbyteCatalog catalog,
                                                                             Map<String, TableInfoInternal> tableNameToTable,
                                                                             JdbcStateManager stateManager,
                                                                             Instant emittedAt) {
    if (isCdc(config) && shouldUseCDC(catalog)) {
      LOGGER.info("using CDC: {}", true);
      // TODO: Figure out how to set the isCDC of stateManager to true. Its always false
      // State works differently in CDC than it does in convention incremental. The state is written to an
      // offset file that debezium reads from. Then once all records are replicated, we read back that
      // offset file (which will have been updated by debezium) and set it in the state. There is no
      // incremental updating of the state structs in the CDC impl.
      final AirbyteFileOffsetBackingStore offsetManager = initializeState(stateManager);
      AirbyteSchemaHistoryStorage schemaHistoryManager = initializeDBHistory(stateManager);
      FilteredFileDatabaseHistory.setDatabaseName(config.get("database").asText());

      final Lsn targetLsn = getLsn(database);
      LOGGER.info("identified target lsn: " + targetLsn);

      /**
       * We use 100,000 as capacity. We've used default * 10 queue size and batch size of debezium :
       * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_BATCH_SIZE} is 2048 (so 20,480)
       * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_QUEUE_SIZE} is 8192 (so 81,920)
       */
      final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>(100000);
      final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(config, catalog, offsetManager, schemaHistoryManager);
      publisher.start(queue);

      // handle state machine around pub/sub logic.
      final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator(
          queue,
          targetLsn,
          publisher::hasClosed,
          publisher::close);

      // convert to airbyte message.
      final AutoCloseableIterator<AirbyteMessage> messageIterator = AutoCloseableIterators
          .transform(
              eventIterator,
              (event) -> DebeziumEventUtils.toAirbyteMessage(event, emittedAt));

      // our goal is to get the state at the time this supplier is called (i.e. after all message records
      // have been produced)
      final Supplier<AirbyteMessage> stateMessageSupplier = () -> {
        Map<String, String> offset = offsetManager.readMap();
        String dbHistory = schemaHistoryManager.read();

        Map<String, Object> state = new HashMap<>();
        state.put(MSSQL_CDC_OFFSET, offset);
        state.put(MSSQL_DB_HISTORY, dbHistory);

        final JsonNode asJson = Jsons.jsonNode(state);

        LOGGER.info("debezium state: {}", asJson);

        CdcState cdcState = new CdcState().withState(asJson);
        stateManager.getCdcStateManager().setCdcState(cdcState);
        final AirbyteStateMessage stateMessage = stateManager.emit();
        return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);

      };

      // wrap the supplier in an iterator so that we can concat it to the message iterator.
      final Iterator<AirbyteMessage> stateMessageIterator = MoreIterators.singletonIteratorFromSupplier(stateMessageSupplier);

      // this structure guarantees that the debezium engine will be closed, before we attempt to emit the
      // state file. we want this so that we have a guarantee that the debezium offset file (which we use
      // to produce the state file) is up-to-date.
      final CompositeIterator<AirbyteMessage> messageIteratorWithStateDecorator = AutoCloseableIterators
          .concatWithEagerClose(messageIterator, AutoCloseableIterators.fromIterator(stateMessageIterator));

      return Collections.singletonList(messageIteratorWithStateDecorator);
    } else {
      LOGGER.info("using CDC: {}", false);
      return super.getIncrementalIterators(config, database, catalog, tableNameToTable, stateManager, emittedAt);
    }
  }

  private static Lsn getLsn(JdbcDatabase database) {
    try {
      final List<JsonNode> jsonNodes = database
          .bufferedResultSetQuery(conn -> conn.createStatement().executeQuery(
              "SELECT sys.fn_cdc_get_max_lsn() AS max_lsn;"), JdbcUtils::rowToJson);

      Preconditions.checkState(jsonNodes.size() == 1);
      if (jsonNodes.get(0).get("max_lsn") != null) {
        return Lsn.valueOf(jsonNodes.get(0).get("max_lsn").binaryValue());
      } else {
        throw new RuntimeException("Max LSN is null, see docs"); // todo: make this error way better
      }
    } catch (SQLException | IOException e) {
      throw new RuntimeException(e);
    }

  }

  private static boolean isCdc(JsonNode config) {
    return config.hasNonNull("replication_method")
        && ReplicationMethod.valueOf(config.get("replication_method").asText())
            .equals(ReplicationMethod.CDC);
  }

  private static boolean shouldUseCDC(ConfiguredAirbyteCatalog catalog) {
    Optional<SyncMode> any = catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode)
        .filter(syncMode -> syncMode == SyncMode.INCREMENTAL).findAny();
    return any.isPresent();
  }

  // Note: in place mutation.
  private static AirbyteStream removeIncrementalWithoutPk(AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      stream.getSupportedSyncModes().remove(SyncMode.INCREMENTAL);
    }

    return stream;
  }

  // Note: in place mutation.
  private static AirbyteStream setIncrementalToSourceDefined(AirbyteStream stream) {
    if (stream.getSupportedSyncModes().contains(SyncMode.INCREMENTAL)) {
      stream.setSourceDefinedCursor(true);
    }

    return stream;
  }

  // Note: in place mutation.
  private static AirbyteStream addCdcMetadataColumns(AirbyteStream stream) {

    ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    properties.set(CDC_LSN, numberType);
    properties.set(CDC_UPDATED_AT, numberType);
    properties.set(CDC_DELETED_AT, numberType);

    return stream;
  }

  private void readSsl(JsonNode sslMethod, List<String> additionalParameters) {
    JsonNode config = sslMethod.get("ssl_method");
    switch (config.get("ssl_method").asText()) {
      case "unencrypted" -> additionalParameters.add("encrypt=false");
      case "encrypted_trust_server_certificate" -> {
        additionalParameters.add("encrypt=true");
        additionalParameters.add("trustServerCertificate=true");
      }
      case "encrypted_verify_certificate" -> {
        additionalParameters.add("encrypt=true");

        // trust store location code found at https://stackoverflow.com/a/56570588
        String trustStoreLocation = Optional.ofNullable(System.getProperty("javax.net.ssl.trustStore"))
            .orElseGet(() -> System.getProperty("java.home") + "/lib/security/cacerts");
        File trustStoreFile = new File(trustStoreLocation);
        if (!trustStoreFile.exists()) {
          throw new RuntimeException(
              "Unable to locate the Java TrustStore: the system property javax.net.ssl.trustStore is undefined or "
                  + trustStoreLocation + " does not exist.");
        }
        String trustStorePassword = System.getProperty("javax.net.ssl.trustStorePassword");
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

  public static void main(String[] args) throws Exception {
    final Source source = new MssqlSource();
    LOGGER.info("starting source: {}", MssqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MssqlSource.class);
  }

  public enum ReplicationMethod {
    STANDARD,
    CDC
  }

}
