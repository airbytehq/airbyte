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

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import io.debezium.engine.ChangeEvent;
import io.debezium.engine.DebeziumEngine;
import io.debezium.engine.format.Json;
import io.debezium.engine.spi.OffsetCommitPolicy;
import java.util.Optional;
import java.util.Properties;
import java.util.Queue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Collectors;
import org.codehaus.plexus.util.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The purpose of this class is to intiliaze and spawn the debezium engine with the right properties
 * to fetch records
 */
public class DebeziumRecordPublisher implements AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumRecordPublisher.class);
  private final ExecutorService executor;
  private DebeziumEngine<ChangeEvent<String, String>> engine;

  private final JsonNode config;
  private final AirbyteFileOffsetBackingStore offsetManager;
  private final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager;

  private final AtomicBoolean hasClosed;
  private final AtomicBoolean isClosing;
  private final AtomicReference<Throwable> thrownError;
  private final CountDownLatch engineLatch;
  private final Properties properties;
  private final ConfiguredAirbyteCatalog catalog;

  public DebeziumRecordPublisher(Properties properties,
                                 JsonNode config,
                                 ConfiguredAirbyteCatalog catalog,
                                 AirbyteFileOffsetBackingStore offsetManager,
                                 Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager) {
    this.properties = properties;
    this.config = config;
    this.catalog = catalog;
    this.offsetManager = offsetManager;
    this.schemaHistoryManager = schemaHistoryManager;
    this.hasClosed = new AtomicBoolean(false);
    this.isClosing = new AtomicBoolean(false);
    this.thrownError = new AtomicReference<>();
    this.executor = Executors.newSingleThreadExecutor();
    this.engineLatch = new CountDownLatch(1);
  }

  public void start(Queue<ChangeEvent<String, String>> queue) {
    engine = DebeziumEngine.create(Json.class)
        .using(getDebeziumProperties())
        .using(new OffsetCommitPolicy.AlwaysCommitOffsetPolicy())
        .notifying(e -> {
          // debezium outputs a tombstone event that has a value of null. this is an artifact of how it
          // interacts with kafka. we want to ignore it.
          // more on the tombstone:
          // https://debezium.io/documentation/reference/configuration/event-flattening.html
          if (e.value() != null) {
            boolean inserted = false;
            while (!inserted) {
              inserted = queue.offer(e);
              if (!inserted) {
                try {
                  Thread.sleep(10);
                } catch (InterruptedException interruptedException) {
                  throw new RuntimeException(interruptedException);
                }
              }
            }
          }
        })
        .using((success, message, error) -> {
          LOGGER.info("Debezium engine shutdown.");
          thrownError.set(error);
          engineLatch.countDown();
        })
        .build();

    // Run the engine asynchronously ...
    executor.execute(engine);
  }

  public boolean hasClosed() {
    return hasClosed.get();
  }

  public void close() throws Exception {
    if (isClosing.compareAndSet(false, true)) {
      // consumers should assume records can be produced until engine has closed.
      if (engine != null) {
        engine.close();
      }

      // wait for closure before shutting down executor service
      engineLatch.await(5, TimeUnit.MINUTES);

      // shut down and await for thread to actually go down
      executor.shutdown();
      executor.awaitTermination(5, TimeUnit.MINUTES);

      // after the engine is completely off, we can mark this as closed
      hasClosed.set(true);

      if (thrownError.get() != null) {
        throw new RuntimeException(thrownError.get());
      }
    }
  }

  protected Properties getDebeziumProperties() {
    final Properties props = new Properties();
    props.putAll(properties);

    // debezium engine configuration
    props.setProperty("name", "engine");
    props.setProperty("offset.storage", "org.apache.kafka.connect.storage.FileOffsetBackingStore");
    props.setProperty("offset.storage.file.filename", offsetManager.getOffsetFilePath().toString());
    props.setProperty("offset.flush.interval.ms", "1000"); // todo: make this longer
    // default values from debezium CommonConnectorConfig
    props.setProperty("max.batch.size", "2048");
    props.setProperty("max.queue.size", "8192");

    if (schemaHistoryManager.isPresent()) {
      // https://debezium.io/documentation/reference/1.4/operations/debezium-server.html#debezium-source-database-history-file-filename
      // https://debezium.io/documentation/reference/development/engine.html#_in_the_code
      // As mentioned in the documents above, debezium connector for MySQL needs to track the schema
      // changes. If we don't do this, we can't fetch records for the table
      // We have implemented our own implementation to filter out the schema information from other
      // databases that the connector is not syncing
      props.setProperty("database.history", "io.airbyte.integrations.debezium.internals.FilteredFileDatabaseHistory");
      props.setProperty("database.history.file.filename", schemaHistoryManager.get().getPath().toString());
    }

    // https://debezium.io/documentation/reference/configuration/avro.html
    props.setProperty("key.converter.schemas.enable", "false");
    props.setProperty("value.converter.schemas.enable", "false");

    // debezium names
    props.setProperty("name", config.get("database").asText());
    props.setProperty("database.server.name", config.get("database").asText());

    // db connection configuration
    props.setProperty("database.hostname", config.get("host").asText());
    props.setProperty("database.port", config.get("port").asText());
    props.setProperty("database.user", config.get("username").asText());
    props.setProperty("database.dbname", config.get("database").asText());

    if (config.has("password")) {
      props.setProperty("database.password", config.get("password").asText());
    }

    // By default "decimal.handing.mode=precise" which's caused returning this value as a binary.
    // The "double" type may cause a loss of precision, so set Debezium's config to store it as a String
    // explicitly in its Kafka messages for more details see:
    // https://debezium.io/documentation/reference/1.4/connectors/postgresql.html#postgresql-decimal-types
    // https://debezium.io/documentation/faq/#how_to_retrieve_decimal_field_from_binary_representation
    props.setProperty("decimal.handling.mode", "string");

    // table selection
    final String tableWhitelist = getTableWhitelist(catalog);
    props.setProperty("table.include.list", tableWhitelist);
    props.setProperty("database.include.list", config.get("database").asText());

    return props;
  }

  @VisibleForTesting
  public static String getTableWhitelist(ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream()
        .filter(s -> s.getSyncMode() == SyncMode.INCREMENTAL)
        .map(ConfiguredAirbyteStream::getStream)
        .map(stream -> stream.getNamespace() + "." + stream.getName())
        // debezium needs commas escaped to split properly
        .map(x -> StringUtils.escape(x, new char[] {','}, "\\,"))
        .collect(Collectors.joining(","));
  }

}
