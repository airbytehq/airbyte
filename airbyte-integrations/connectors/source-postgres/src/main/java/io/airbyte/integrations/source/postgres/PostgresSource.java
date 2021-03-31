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

import static java.lang.Thread.sleep;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.AbstractIterator;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.concurrency.CloseableLinkedBlockingQueue;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Queues;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.PgLsn;
import io.airbyte.db.PostgresUtils;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.db.jdbc.PostgresJdbcStreamingQueryConfiguration;
import io.airbyte.integrations.base.IntegrationRunner;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.JdbcStateManager;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import io.debezium.engine.format.Json;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.sql.SQLException;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.function.Predicate;
import org.apache.commons.lang3.RandomStringUtils;
import org.apache.kafka.connect.data.Struct;
import org.apache.kafka.connect.source.SourceRecord;
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

  enum SnapshotMetadata {
    TRUE,
    FALSE,
    LAST
  }

  private PgLsn extractLsn(ChangeEvent<String, String> event) {
    return Optional.ofNullable(event.value())
        .flatMap(value -> Optional.ofNullable(Jsons.deserialize(value).get("source")))
        .flatMap(source -> Optional.ofNullable(source.get("lsn").asText()))
        .map(Long::parseLong)
        .map(PgLsn::fromLong)
        .orElseThrow(() -> new IllegalStateException("Could not find LSN"));
  }

  private SnapshotMetadata getSnapshotMetadata(ChangeEvent<String, String> event) {
    try {
      final Method sourceRecordMethod = event.getClass().getMethod("sourceRecord");
      sourceRecordMethod.setAccessible(true);
      final SourceRecord sourceRecord = (SourceRecord) sourceRecordMethod.invoke(event);
      final String snapshot = ((Struct) sourceRecord.value()).getStruct("source").getString("snapshot");
      // the snapshot field is an enum of true, false, and last.
      return SnapshotMetadata.valueOf(snapshot.toUpperCase());
    } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
      throw new RuntimeException(e);
    }
  }

  private Predicate<ChangeEvent<String, String>> getTerminationPredicate(JdbcDatabase database) {
    final PgLsn targetLsn = getLsn(database);
    LOGGER.info("identified target lsn: " + targetLsn);

    return (event) -> {
      final PgLsn eventLsn = extractLsn(event);
      final SnapshotMetadata snapshotMetadata = getSnapshotMetadata(event);

      if (targetLsn.compareTo(eventLsn) > 0) {
        return false;
      } else {
        // if not snapshot or is snapshot but last record in snapshot.
        return SnapshotMetadata.TRUE != snapshotMetadata;
      }
    };
  }

  private static class DebeziumPayload {

    private final ChangeEvent<String, String> changeEvent;
    private final AirbyteMessage message;

    public DebeziumPayload(final ChangeEvent<String, String> changeEvent, final AirbyteMessage recordMessage) {
      this.changeEvent = changeEvent;
      this.message = recordMessage;
    }

    public ChangeEvent<String, String> getChangeEvent() {
      return changeEvent;
    }

    public AirbyteMessage getMessage() {
      return message;
    }

  }

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(JsonNode config,
                                                                             JdbcDatabase database,
                                                                             ConfiguredAirbyteCatalog catalog,
                                                                             Map<String, TableInfoInternal> tableNameToTable,
                                                                             JdbcStateManager stateManager,
                                                                             Instant emittedAt) {
    if (isCdc(config)) {
      final Predicate<ChangeEvent<String, String>> hasReachedLsnPredicate = getTerminationPredicate(database);
      AtomicReference<Throwable> thrownError = new AtomicReference<>();
      AtomicBoolean completed = new AtomicBoolean(false);
      ExecutorService executor = Executors.newSingleThreadExecutor();
      final CloseableLinkedBlockingQueue<DebeziumPayload> queue = new CloseableLinkedBlockingQueue<>(executor::shutdown);

      DebeziumEngine<ChangeEvent<String, String>> engine = DebeziumEngine.create(Json.class)
          .using(getDebeziumProperties(config))
          .notifying(event -> {
            try {
              final AirbyteMessage message = convertChangeEvent(event, emittedAt);
              queue.add(new DebeziumPayload(event, message));
            } catch (Exception e) {
              LOGGER.info("error: " + e);
              thrownError.set(e);
            }
          })
          .using((success, message, error) -> {
            LOGGER.info("completed!");
            completed.set(true);
            thrownError.set(error);
          })
          .build();

      // Run the engine asynchronously ...
      executor.execute(engine);

      final Iterator<DebeziumPayload> queueIterator = Queues.toStream(queue).iterator();
      final AbstractIterator<DebeziumPayload> iterator = new AbstractIterator<>() {

        private boolean hasReachedLsn = false;

        @Override
        protected DebeziumPayload computeNext() {
          // if we have reached the lsn we stop, otherwise we have the potential to wait indefinitely for the
          // next value.
          if (!hasReachedLsn) {
            while (!queueIterator.hasNext()) {
              LOGGER.info("sleeping.");
              try {
                sleep(5000);
              } catch (InterruptedException e) {
                throw new RuntimeException(e);
              }
            }

            final DebeziumPayload next = queueIterator.next();
            LOGGER.info("next {}", next);
            // todo fix this cast. the record passed to this iterator has to include the lsn somewhere. it can
            // either be the full change event or some smaller object that just includes the lsn.
            // we guarantee that this will always eventually return true, because we pick an LSN that already
            // exists when we start the sync.
            if (hasReachedLsnPredicate.test(next.getChangeEvent())) {
              hasReachedLsn = true;
            }
            return next;
          } else {
            return endOfData();
          }
        }

      };

      final AutoCloseableIterator<DebeziumPayload> payloadIterator = AutoCloseableIterators.fromIterator(iterator, () -> {
        engine.close();
        executor.shutdown();

        if (thrownError.get() != null) {
          throw new RuntimeException(thrownError.get());
        }
      });

      final AutoCloseableIterator<AirbyteMessage> messageIterator = AutoCloseableIterators.transform(payloadIterator, DebeziumPayload::getMessage);

      return Collections.singletonList(messageIterator);
    } else {
      return super.getIncrementalIterators(config, database, catalog, tableNameToTable, stateManager, emittedAt);
    }
  }

  // todo: make this use catalog as well
  // todo: make this use the state for the files as well
  protected static Properties getDebeziumProperties(JsonNode config) {
    final Properties props = new Properties();
    props.setProperty("name", "engine");
    props.setProperty("plugin.name", "pgoutput");
    props.setProperty("connector.class", "io.debezium.connector.postgresql.PostgresConnector");
    props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
    props.setProperty("offset.storage.file.filename", "/tmp/offsets-" + RandomStringUtils.randomAlphabetic(5) + ".dat");
    props.setProperty("offset.flush.interval.ms", "1000"); // todo: make this longer

    // https://debezium.io/documentation/reference/configuration/avro.html
    props.setProperty("key.converter.schemas.enable", "false");
    props.setProperty("value.converter.schemas.enable", "false");

    // https://debezium.io/documentation/reference/configuration/event-flattening.html
    props.setProperty("delete.handling.mode", "rewrite");
    props.setProperty("drop.tombstones", "false");
    props.setProperty("transforms.unwrap.type", "io.debezium.transforms.ExtractNewRecordState");

    // props.setProperty("table.include.list", "public.id_and_name"); // todo
    props.setProperty("database.include.list", config.get("database").asText());
    props.setProperty("name", "orders-postgres-connector");
    props.setProperty("include_schema_changes", "true");
    props.setProperty("database.server.name", "orders"); // todo
    props.setProperty("database.hostname", config.get("host").asText());
    props.setProperty("database.port", config.get("port").asText());
    props.setProperty("database.user", config.get("username").asText());

    if (config.has("password")) {
      props.setProperty("database.password", config.get("password").asText());
    }

    props.setProperty("database.dbname", config.get("database").asText());
    props.setProperty("database.history", "io.debezium.relational.history.FileDatabaseHistory"); // todo: any reason not to use in memory version and
    // reload from
    props.setProperty("database.history.file.filename", "/tmp/debezium/dbhistory-" + RandomStringUtils.randomAlphabetic(5) + ".dat");

    props.setProperty("slot.name", config.get("replication_slot").asText());

    props.setProperty("snapshot.mode", "exported"); // can use never if we want to manage full refreshes ourselves

    return props;
  }

  private static boolean isCdc(JsonNode config) {
    LOGGER.info("isCdc config: " + config);
    return !(config.get("replication_slot") == null);
  }

  public static AirbyteMessage convertChangeEvent(ChangeEvent<String, String> event, Instant emittedAt) {
    final JsonNode debeziumRecord = Jsons.deserialize(event.value());
    final JsonNode before = debeziumRecord.get("before");
    final JsonNode after = debeziumRecord.get("after");
    final JsonNode source = debeziumRecord.get("source");

    final JsonNode data = formatDebeziumData(before, after, source);

    final String streamName = source.get("table").asText();

    final AirbyteRecordMessage airbyteRecordMessage = new AirbyteRecordMessage()
        .withStream(streamName)
        .withEmittedAt(emittedAt.toEpochMilli())
        .withData(data);

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(airbyteRecordMessage);
  }

  public static JsonNode formatDebeziumData(JsonNode before, JsonNode after, JsonNode source) {
    final ObjectNode base = (ObjectNode) (after.isNull() ? before : after);

    long transactionMillis = source.get("ts_ms").asLong();
    long lsn = source.get("lsn").asLong();

    base.put("_ab_cdc_updated_at", transactionMillis);
    base.put("_ab_cdc_lsn", lsn);

    if (after.isNull()) {
      base.put("_ab_cdc_deleted_at", transactionMillis);
    } else {
      base.put("_ab_cdc_deleted_at", (Long) null);
    }

    return base;
  }

  public static void main(String[] args) throws Exception {
    final Source source = new PostgresSource();
    LOGGER.info("starting source: {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSource.class);
  }

}
