/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.CompositeIterator;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.debezium.internals.AirbyteFileOffsetBackingStore;
import io.airbyte.integrations.debezium.internals.AirbyteSchemaHistoryStorage;
import io.airbyte.integrations.debezium.internals.DebeziumEventUtils;
import io.airbyte.integrations.debezium.internals.DebeziumRecordIterator;
import io.airbyte.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.integrations.debezium.internals.FilteredFileDatabaseHistory;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import io.debezium.engine.ChangeEvent;
import java.time.Instant;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Properties;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class acts as the bridge between Airbyte DB connectors and debezium. If a DB connector wants
 * to use debezium for CDC, it should use this class
 */
public class AirbyteDebeziumHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteDebeziumHandler.class);
  /**
   * We use 10000 as capacity cause the default queue size and batch size of debezium is :
   * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_BATCH_SIZE}is 2048
   * {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_QUEUE_SIZE} is 8192
   */
  private static final int QUEUE_CAPACITY = 10000;

  private final Properties connectorProperties;
  private final JsonNode config;
  private final CdcTargetPosition targetPosition;
  private final ConfiguredAirbyteCatalog catalog;
  private final boolean trackSchemaHistory;

  private final LinkedBlockingQueue<ChangeEvent<String, String>> queue;

  public AirbyteDebeziumHandler(final JsonNode config,
                                final CdcTargetPosition targetPosition,
                                final Properties connectorProperties,
                                final ConfiguredAirbyteCatalog catalog,
                                final boolean trackSchemaHistory) {
    this.config = config;
    this.targetPosition = targetPosition;
    this.connectorProperties = connectorProperties;
    this.catalog = catalog;
    this.trackSchemaHistory = trackSchemaHistory;
    this.queue = new LinkedBlockingQueue<>(QUEUE_CAPACITY);
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(final CdcSavedInfoFetcher cdcSavedInfoFetcher,
                                                                             final CdcStateHandler cdcStateHandler,
                                                                             final CdcMetadataInjector cdcMetadataInjector,
                                                                             final Instant emittedAt) {
    LOGGER.info("using CDC: {}", true);
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(cdcSavedInfoFetcher.getSavedOffset());
    final Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager = schemaHistoryManager(cdcSavedInfoFetcher);
    final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(connectorProperties, config, catalog, offsetManager,
        schemaHistoryManager);
    publisher.start(queue);

    // handle state machine around pub/sub logic.
    final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator(
        queue,
        targetPosition,
        publisher::hasClosed,
        publisher::close);

    // convert to airbyte message.
    final AutoCloseableIterator<AirbyteMessage> messageIterator = AutoCloseableIterators
        .transform(
            eventIterator,
            (event) -> DebeziumEventUtils.toAirbyteMessage(event, cdcMetadataInjector, emittedAt));

    // our goal is to get the state at the time this supplier is called (i.e. after all message records
    // have been produced)
    final Supplier<AirbyteMessage> stateMessageSupplier = () -> {
      final Map<String, String> offset = offsetManager.read();
      final String dbHistory = trackSchemaHistory ? schemaHistoryManager
          .orElseThrow(() -> new RuntimeException("Schema History Tracking is true but manager is not initialised")).read() : null;

      return cdcStateHandler.saveState(offset, dbHistory);
    };

    // wrap the supplier in an iterator so that we can concat it to the message iterator.
    final Iterator<AirbyteMessage> stateMessageIterator = MoreIterators.singletonIteratorFromSupplier(stateMessageSupplier);

    // this structure guarantees that the debezium engine will be closed, before we attempt to emit the
    // state file. we want this so that we have a guarantee that the debezium offset file (which we use
    // to produce the state file) is up-to-date.
    final CompositeIterator<AirbyteMessage> messageIteratorWithStateDecorator =
        AutoCloseableIterators.concatWithEagerClose(messageIterator, AutoCloseableIterators.fromIterator(stateMessageIterator));

    return Collections.singletonList(messageIteratorWithStateDecorator);
  }

  private Optional<AirbyteSchemaHistoryStorage> schemaHistoryManager(final CdcSavedInfoFetcher cdcSavedInfoFetcher) {
    if (trackSchemaHistory) {
      FilteredFileDatabaseHistory.setDatabaseName(config.get(JdbcUtils.DATABASE_KEY).asText());
      return Optional.of(AirbyteSchemaHistoryStorage.initializeDBHistory(cdcSavedInfoFetcher.getSavedSchemaHistory()));
    }

    return Optional.empty();
  }

  public static boolean shouldUseCDC(final ConfiguredAirbyteCatalog catalog) {
    return catalog.getStreams().stream().map(ConfiguredAirbyteStream::getSyncMode)
        .anyMatch(syncMode -> syncMode == SyncMode.INCREMENTAL);
  }

}
