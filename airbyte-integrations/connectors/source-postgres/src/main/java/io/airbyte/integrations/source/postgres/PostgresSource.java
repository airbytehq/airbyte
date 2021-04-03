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

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.CompositeIterator;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.PgLsn;
import io.airbyte.db.PostgresUtils;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.PostgresJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.JdbcStateManager;
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
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.codehaus.plexus.util.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresSource extends AbstractJdbcSource implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresSource.class);

  static final String DRIVER_CLASS = "org.postgresql.Driver";

  public PostgresSource() {
    super(DRIVER_CLASS, new PostgresJdbcStreamingQueryConfiguration());
  }

  @Override
  public JsonNode toJdbcConfig(JsonNode config) {
    final ImmutableMap.Builder<Object, Object> configBuilder = ImmutableMap.builder()
        .put("username", config.get("username").asText())
        .put("jdbc_url", String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()));

    if (config.has("password")) {
      configBuilder.put("password", config.get("password").asText());
    }

    return Jsons.jsonNode(configBuilder.build());
  }

  @Override
  public Set<String> getExcludedInternalSchemas() {
    return Set.of("information_schema", "pg_catalog", "pg_internal", "catalog_history");
  }

  @Override
  public AirbyteCatalog discover(JsonNode config) throws Exception {
    AirbyteCatalog catalog = super.discover(config);

    if (isCdc(config)) {
      final List<AirbyteStream> streams = catalog.getStreams().stream()
          .map(PostgresSource::removeIncrementalWithoutPk)
          .map(PostgresSource::addCdcMetadataColumns)
          .collect(Collectors.toList());

      catalog.setStreams(streams);
    }

    return catalog;
  }

  @Override
  public List<CheckedConsumer<JdbcDatabase, Exception>> getCheckOperations(JsonNode config) throws Exception {
    final List<CheckedConsumer<JdbcDatabase, Exception>> checkOperations = new ArrayList<>(super.getCheckOperations(config));

    if (isCdc(config)) {
      checkOperations.add(database -> database.query(connection -> {
        final String replicationSlot = config.get("replication_slot").asText();
        // todo: we can't use enquoteIdentifier since this isn't an identifier, it's a value. fix this to
        // prevent sql injection
        final String sql =
            String.format("SELECT slot_name, plugin, database FROM pg_replication_slots WHERE slot_name = '%s' AND plugin = '%s' AND database = '%s'",
                replicationSlot,
                "pgoutput",
                config.get("database").asText());

        LOGGER.info("Attempting to find the named replication slot using the query: " + sql);

        return connection.prepareStatement(sql);
      }, JdbcUtils::rowToJson));
    }

    return checkOperations;
  }

  private static PgLsn getLsn(JdbcDatabase database) {
    try {
      return PostgresUtils.getLsn(database);
    } catch (SQLException e) {
      throw new RuntimeException(e);
    }
  }

  private AirbyteFileOffsetBackingStore initializeState(JdbcStateManager stateManager) {
    final Path cdcWorkingDir;
    try {
      cdcWorkingDir = Files.createTempDirectory(Path.of("/tmp"), "cdc");
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    final Path cdcOffsetFilePath = cdcWorkingDir.resolve("offset.dat");

    final AirbyteFileOffsetBackingStore offsetManager = new AirbyteFileOffsetBackingStore(cdcOffsetFilePath);
    offsetManager.persist(stateManager.getCdcStateManager().getCdcState());
    return offsetManager;
  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(JsonNode config,
                                                                             JdbcDatabase database,
                                                                             ConfiguredAirbyteCatalog catalog,
                                                                             Map<String, TableInfoInternal> tableNameToTable,
                                                                             JdbcStateManager stateManager,
                                                                             Instant emittedAt) {
    if (isCdc(config)) {
      // State works differently in CDC than it does in convention incremental. The state is written to an
      // offset file that debezium reads from. Then once all records are replicated, we read back that
      // offset file (which will have been updated by debezium) and set it in the state. There is no
      // incremental updating of the state structs in the CDC impl.
      final AirbyteFileOffsetBackingStore offsetManager = initializeState(stateManager);

      final PgLsn targetLsn = getLsn(database);
      LOGGER.info("identified target lsn: " + targetLsn);

      final LinkedBlockingQueue<ChangeEvent<String, String>> queue = new LinkedBlockingQueue<>();

      final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(config, catalog, offsetManager);
      publisher.start(queue);

      // handle state machine around pub/sub logic.
      final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator(
          queue,
          targetLsn,
          publisher::hasClosed,
          publisher::close);

      // convert to airbyte message.
      final AutoCloseableIterator<AirbyteMessage> messageIterator = AutoCloseableIterators.transform(
          eventIterator,
          (event) -> DebeziumEventUtils.toAirbyteMessage(event, emittedAt));

      // our goal is to get the state at the time this supplier is called (i.e. after all message records
      // have been produced)
      final Supplier<AirbyteMessage> stateMessageSupplier = () -> {
        stateManager.getCdcStateManager().setCdcState(offsetManager.read());
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
      return super.getIncrementalIterators(config, database, catalog, tableNameToTable, stateManager, emittedAt);
    }
  }

  protected static String getTableWhitelist(ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream()
        .map(ConfiguredAirbyteStream::getStream)
        .map(AirbyteStream::getName)
        // debezium needs commas escaped to split properly
        .map(x -> StringUtils.escape(x, new char[] {','}, "\\,"))
        .collect(Collectors.joining(","));

  }

  private static boolean isCdc(JsonNode config) {
    LOGGER.info("isCdc config: " + config);
    return !(config.get("replication_slot") == null);
  }

  /*
   * It isn't possible to recreate the state of the original database unless we include extra
   * information (like an oid) when using logical replication. By limiting to Full Refresh when we
   * don't have a primary key we dodge the problem for now. As a work around a CDC and non-CDC source
   * could be configured if there's a need to replicate a large non-PK table.
   */
  private static AirbyteStream removeIncrementalWithoutPk(AirbyteStream stream) {
    if (stream.getSourceDefinedPrimaryKey().isEmpty()) {
      stream.getSupportedSyncModes().remove(SyncMode.INCREMENTAL);
    }

    return stream;
  }

  private static AirbyteStream addCdcMetadataColumns(AirbyteStream stream) {
    ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    ObjectNode properties = (ObjectNode) jsonSchema.get("properties");

    final JsonNode numberType = Jsons.jsonNode(ImmutableMap.of("type", "number"));
    properties.set("_ab_cdc_lsn", numberType);
    properties.set("_ab_cdc_updated_at", numberType);
    properties.set("_ab_cdc_deleted_at", numberType);

    return stream;
  }

  public static void main(String[] args) throws Exception {
    final Source source = new PostgresSource();
    LOGGER.info("starting source: {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSource.class);
  }

}
