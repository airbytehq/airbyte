package io.airbyte.integrations.source.debezium;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.commons.util.CompositeIterator;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.integrations.source.debezium.interfaces.CdcConnectorMetadata;
import io.airbyte.integrations.source.debezium.interfaces.CdcSavedInfo;
import io.airbyte.integrations.source.debezium.interfaces.CdcStateHandler;
import io.airbyte.integrations.source.debezium.interfaces.CdcTargetPosition;
import io.airbyte.protocol.models.AirbyteMessage;
import io.debezium.engine.ChangeEvent;
import java.time.Instant;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DebeziumInit {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumInit.class);
  /**
   * We use 10000 as capacity cause the default queue size and batch size of debezium is : {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_BATCH_SIZE}is
   * 2048 {@link io.debezium.config.CommonConnectorConfig#DEFAULT_MAX_QUEUE_SIZE} is 8192
   */
  private static final int QUEUE_CAPACITY = 10000;

  private final Properties connectorProperties;
  private final JsonNode config;
  private final CdcTargetPosition cdcTargetPosition;
  private final List<String> tablesToSync;
  private final boolean trackSchemaHistory;

  private final LinkedBlockingQueue<ChangeEvent<String, String>> queue;

  public DebeziumInit(JsonNode config, CdcTargetPosition cdcTargetPosition, Properties connectorProperties,
      List<String> tablesToSync, boolean trackSchemaHistory) {
    this.config = config;
    this.cdcTargetPosition = cdcTargetPosition;
    this.connectorProperties = connectorProperties;
    this.tablesToSync = tablesToSync;
    this.trackSchemaHistory = trackSchemaHistory;
    this.queue = new LinkedBlockingQueue<>(QUEUE_CAPACITY);
  }

  public List<AutoCloseableIterator<AirbyteMessage>> getIncrementalIterators(
      CdcSavedInfo cdcSavedInfo,
      CdcStateHandler cdcStateHandler,
      CdcConnectorMetadata cdcConnectorMetadata,
      Instant emittedAt) {
    LOGGER.info("using CDC: {}", true);
    // TODO: Figure out how to set the isCDC of stateManager to true. Its always false
    final AirbyteFileOffsetBackingStore offsetManager = AirbyteFileOffsetBackingStore.initializeState(cdcSavedInfo.getSavedOffset());
    final AirbyteSchemaHistoryStorage schemaHistoryManager = schemaHistoryManager(cdcSavedInfo);
    final DebeziumRecordPublisher publisher = new DebeziumRecordPublisher(connectorProperties, config, tablesToSync, offsetManager,
        schemaHistoryManager);
    publisher.start(queue);

    // handle state machine around pub/sub logic.
    final AutoCloseableIterator<ChangeEvent<String, String>> eventIterator = new DebeziumRecordIterator(
        queue,
        cdcTargetPosition,
        publisher::hasClosed,
        publisher::close);

    // convert to airbyte message.
    final AutoCloseableIterator<AirbyteMessage> messageIterator = AutoCloseableIterators
        .transform(
            eventIterator,
            (event) -> DebeziumEventUtils.toAirbyteMessage(event, cdcConnectorMetadata, emittedAt));

    // our goal is to get the state at the time this supplier is called (i.e. after all message records
    // have been produced)
    final Supplier<AirbyteMessage> stateMessageSupplier = () -> {
      Map<String, String> offset = offsetManager.read();
      String dbHistory = trackSchemaHistory ? schemaHistoryManager.read() : null;

      return cdcStateHandler.state(offset, dbHistory);
    };

    // wrap the supplier in an iterator so that we can concat it to the message iterator.
    final Iterator<AirbyteMessage> stateMessageIterator = MoreIterators.singletonIteratorFromSupplier(stateMessageSupplier);

    // this structure guarantees that the debezium engine will be closed, before we attempt to emit the
    // state file. we want this so that we have a guarantee that the debezium offset file (which we use
    // to produce the state file) is up-to-date.
    final CompositeIterator<AirbyteMessage> messageIteratorWithStateDecorator = AutoCloseableIterators.concatWithEagerClose(messageIterator, AutoCloseableIterators.fromIterator(stateMessageIterator));

    return Collections.singletonList(messageIteratorWithStateDecorator);
  }

  private AirbyteSchemaHistoryStorage schemaHistoryManager(CdcSavedInfo cdcSavedInfo) {
    if (trackSchemaHistory) {
      FilteredFileDatabaseHistory.setDatabaseName(config.get("database").asText());
      return AirbyteSchemaHistoryStorage.initializeDBHistory(cdcSavedInfo.getSavedSchemaHistory());
    }

    return null;
  }

}
