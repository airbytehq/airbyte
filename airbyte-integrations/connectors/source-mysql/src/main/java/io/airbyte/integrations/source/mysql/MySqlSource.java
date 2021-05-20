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

package io.airbyte.integrations.source.mysql;

import static java.util.stream.Collectors.toList;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.CompositeIterator;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.jdbc.JdbcDatabase;
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
import io.debezium.engine.ChangeEvent;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Instant;
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

public class MySqlSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlSource.class);

  public static final String DRIVER_CLASS = "com.mysql.cj.jdbc.Driver";
  public static final String MYSQL_CDC_OFFSET = "mysql_cdc_offset";
  public static final String MYSQL_DB_HISTORY = "mysql_db_history";

  public MySqlSource() {
    super(DRIVER_CLASS, new MySqlJdbcStreamingQueryConfiguration());
  }

  private static AirbyteStream removeIncrementalWithoutPk(AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      stream.getSupportedSyncModes().remove(SyncMode.INCREMENTAL);
    }

    return stream;
  }

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
    final JsonNode stringType = Jsons.jsonNode(ImmutableMap.of("type", "string"));
    properties.set(CDC_LOG_FILE, stringType);
    properties.set(CDC_LOG_POS, numberType);
    properties.set(CDC_UPDATED_AT, numberType);
    properties.set(CDC_DELETED_AT, numberType);

    return stream;
  }

  @Override
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    AirbyteCatalog catalog = super.discover(config);

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
  public JsonNode toJdbcConfig(JsonNode config) {
    final StringBuilder jdbc_url = new StringBuilder(String.format("jdbc:mysql://%s:%s/%s",
        config.get("host").asText(),
        config.get("port").asText(),
        config.get("database").asText()));
    // see MySqlJdbcStreamingQueryConfiguration for more context on why useCursorFetch=true is needed.
    jdbc_url.append("?useCursorFetch=true");
    if (config.get("jdbc_url_params") != null && !config.get("jdbc_url_params").asText().isEmpty()) {
      jdbc_url.append("&").append(config.get("jdbc_url_params").asText());
    }
    ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", jdbc_url.toString());

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  private static boolean isCdc(JsonNode config) {
    final boolean isCdc = config.hasNonNull("replication_method")
        && ReplicationMethod.valueOf(config.get("replication_method").asText())
            .equals(ReplicationMethod.CDC);

    return isCdc;
  }

  static boolean shouldUseCDC(ConfiguredAirbyteCatalog catalog) {
    Optional<SyncMode> any = catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode)
        .filter(syncMode -> syncMode == SyncMode.INCREMENTAL).findAny();
    return any.isPresent();
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
      final AirbyteFileOffsetBackingStore offsetManager = initializeState(stateManager);
      AirbyteFileDatabaseHistoryStorageOperations dbHistoryStorageManager = initializeDBHistory(
          stateManager);
      FilteredFileDatabaseHistory.setDatabaseName(config.get("database").asText());
      final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>();
      final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(config, catalog,
          offsetManager, dbHistoryStorageManager);
      publisher.start(queue);

      // handle state machine around pub/sub logic.
      final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator(
          queue,
          // targetLsn,
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
        String dbHistory = dbHistoryStorageManager.read();

        Map<String, Object> state = new HashMap<>();
        state.put(MYSQL_CDC_OFFSET, offset);
        state.put(MYSQL_DB_HISTORY, dbHistory);

        final JsonNode asJson = Jsons.jsonNode(state);

        LOGGER.info("debezium state: {}", asJson);

        CdcState cdcState = new CdcState().withState(asJson);
        stateManager.getCdcStateManager().setCdcState(cdcState);
        final AirbyteStateMessage stateMessage = stateManager.emit();
        return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);

      };

      // wrap the supplier in an iterator so that we can concat it to the message iterator.
      final Iterator<AirbyteMessage> stateMessageIterator = MoreIterators
          .singletonIteratorFromSupplier(stateMessageSupplier);

      // this structure guarantees that the debezium engine will be closed, before we attempt to emit the
      // state file. we want this so that we have a guarantee that the debezium offset file (which we use
      // to produce the state file) is up-to-date.
      final CompositeIterator<AirbyteMessage> messageIteratorWithStateDecorator = AutoCloseableIterators
          .concatWithEagerClose(messageIterator,
              AutoCloseableIterators.fromIterator(stateMessageIterator));

      return Collections.singletonList(messageIteratorWithStateDecorator);
    } else {
      LOGGER.info("using CDC: {}", false);
      return super.getIncrementalIterators(config, database, catalog, tableNameToTable, stateManager,
          emittedAt);
    }
  }

  private AirbyteFileOffsetBackingStore initializeState(JdbcStateManager stateManager) {
    final Path cdcWorkingDir;
    try {
      cdcWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-state-offset");
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    final Path cdcOffsetFilePath = cdcWorkingDir.resolve("offset.dat");

    final AirbyteFileOffsetBackingStore offsetManager = new AirbyteFileOffsetBackingStore(
        cdcOffsetFilePath);
    offsetManager.persist(stateManager.getCdcStateManager().getCdcState());
    return offsetManager;
  }

  private AirbyteFileDatabaseHistoryStorageOperations initializeDBHistory(
                                                                          JdbcStateManager stateManager) {
    final Path dbHistoryWorkingDir;
    try {
      dbHistoryWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc-db-history");
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    final Path dbHistoryFilePath = dbHistoryWorkingDir.resolve("dbhistory.dat");

    final AirbyteFileDatabaseHistoryStorageOperations dbHistoryStorageManager = new AirbyteFileDatabaseHistoryStorageOperations(dbHistoryFilePath);
    dbHistoryStorageManager.persist(stateManager.getCdcStateManager().getCdcState());
    return dbHistoryStorageManager;
  }

  @Override
  public Set<String> getExcludedInternalSchemas() {
    return Set.of(
        "information_schema",
        "mysql",
        "performance_schema",
        "sys");
  }

  public static void main(String[] args) throws Exception {
    final Source source = new MySqlSource();
    LOGGER.info("starting source: {}", MySqlSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", MySqlSource.class);
  }

  public enum ReplicationMethod {
    STANDARD,
    CDC
  }

}
