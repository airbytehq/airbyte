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
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Queues;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
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
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Stream;
import org.apache.commons.lang3.RandomStringUtils;
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

  @Override
  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(JsonNode config,
                                                                             JdbcDatabase database,
                                                                             ConfiguredAirbyteCatalog catalog,
                                                                             Map<String, TableInfoInternal> tableNameToTable,
                                                                             JdbcStateManager stateManager,
                                                                             Instant emittedAt) {
    if (isCdc(config)) {
      AtomicReference<Throwable> thrownError = new AtomicReference<>();
      AtomicBoolean completed = new AtomicBoolean(false);
      ExecutorService executor = Executors.newSingleThreadExecutor();
      CloseableLinkedBlockingQueue queue = new CloseableLinkedBlockingQueue(executor::shutdown);

      DebeziumEngine<ChangeEvent<String, String>> engine = DebeziumEngine.create(Json.class)
          .using(getDebeziumProperties(config))
          .notifying(record -> {
            try {
              LOGGER.info("record = " + record);
              JsonNode node = Jsons.jsonNode(
                  ImmutableMap.of("key", record.key() != null ? record.key() : "null", "value", record.value(), "destination", record.destination())); // todo:
                                                                                                                                                       // better
                                                                                                                                                       // transformation
                                                                                                                                                       // function
                                                                                                                                                       // here
              LOGGER.info("node = " + node);
              queue.add(node);
            } catch (Exception e) {
              LOGGER.info("error");
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

      final Stream<JsonNode> jsonStream = Queues.toStream(queue);
      final AutoCloseableIterator<JsonNode> jsonIterator = AutoCloseableIterators.fromStream(jsonStream);
      final AutoCloseableIterator<AirbyteMessage> messageIterator = AutoCloseableIterators.transform(jsonIterator, r -> new AirbyteMessage()
          .withType(AirbyteMessage.Type.RECORD)
          .withRecord(new AirbyteRecordMessage()
              .withStream("single_stream") // todo: refactor this
              .withEmittedAt(emittedAt.toEpochMilli())
              .withData(r)));

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
    // props.setProperty("database.server.name", "orders"); // todo
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

  public static void main(String[] args) throws Exception {
    final Source source = new PostgresSource();
    LOGGER.info("starting source: {}", PostgresSource.class);
    new IntegrationRunner(source).run(args);
    LOGGER.info("completed source: {}", PostgresSource.class);
  }

}
