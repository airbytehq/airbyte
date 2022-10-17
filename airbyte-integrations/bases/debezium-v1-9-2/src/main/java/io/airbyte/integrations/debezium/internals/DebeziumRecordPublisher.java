/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The purpose of this class is to initialize and spawn the debezium engine with the right
 * properties to fetch records
 */
public class DebeziumRecordPublisher implements AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumRecordPublisher.class);
  private final ExecutorService executor;
  private DebeziumEngine<ChangeEvent<String, String>> engine;
  private final AtomicBoolean hasClosed;
  private final AtomicBoolean isClosing;
  private final AtomicReference<Throwable> thrownError;
  private final CountDownLatch engineLatch;
  private final DebeziumPropertiesManager debeziumPropertiesManager;

  public DebeziumRecordPublisher(final Properties properties,
                                 final JsonNode config,
                                 final ConfiguredAirbyteCatalog catalog,
                                 final AirbyteFileOffsetBackingStore offsetManager,
                                 final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager) {
    this.debeziumPropertiesManager = new DebeziumPropertiesManager(properties, config, catalog, offsetManager,
        schemaHistoryManager);
    this.hasClosed = new AtomicBoolean(false);
    this.isClosing = new AtomicBoolean(false);
    this.thrownError = new AtomicReference<>();
    this.executor = Executors.newSingleThreadExecutor();
    this.engineLatch = new CountDownLatch(1);
  }

  public void start(final Queue<ChangeEvent<String, String>> queue) {
    engine = DebeziumEngine.create(Json.class)
        .using(debeziumPropertiesManager.getDebeziumProperties())
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

}
