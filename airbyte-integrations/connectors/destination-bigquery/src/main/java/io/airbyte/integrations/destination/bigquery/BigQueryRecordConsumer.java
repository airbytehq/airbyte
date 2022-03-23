/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery;

import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.record_buffer.BufferingStrategy;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.Set;
import java.util.function.Consumer;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryRecordConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryRecordConsumer.class);

  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final BufferingStrategy bufferingStrategy;
  private final ConfiguredAirbyteCatalog catalog;
  private final Set<AirbyteStreamNameNamespacePair> streamNames;

  private boolean hasStarted;
  private boolean hasClosed;

  private AirbyteMessage lastFlushedState;
  private AirbyteMessage pendingState;

  public BigQueryRecordConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
                                final BufferingStrategy bufferingStrategy,
                                final ConfiguredAirbyteCatalog catalog) {
    this.bufferingStrategy = bufferingStrategy;
    this.outputRecordCollector = outputRecordCollector;
    this.catalog = catalog;
    this.streamNames = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);

    this.hasStarted = false;
    this.hasClosed = false;

    bufferingStrategy.registerFlushAllEventHook(this::flushQueueToDestination);
  }

  @Override
  protected void startTracked() {
    Preconditions.checkState(!hasStarted, "Consumer has already been started.");
    hasStarted = true;
    LOGGER.info("{} started.", BigQueryRecordConsumer.class);
  }

  @Override
  public void acceptTracked(final AirbyteMessage message) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started");

    if (message.getType() == Type.STATE) {
      pendingState = message;
    } else if (message.getType() == Type.RECORD) {
      processRecord(message);
    } else {
      LOGGER.warn("Unexpected message: {}", message.getType());
    }
  }

  private void processRecord(AirbyteMessage message) throws Exception {
    final AirbyteRecordMessage recordMessage = message.getRecord();
    final AirbyteStreamNameNamespacePair stream = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);
    if (!streamNames.contains(stream)) {
      throwUnrecognizedStream(catalog, message);
    }

    bufferingStrategy.addRecord(stream, message);
  }

  private void flushQueueToDestination() {
    if (pendingState != null) {
      lastFlushedState = pendingState;
      pendingState = null;
    }
  }

  private void throwUnrecognizedStream(final ConfiguredAirbyteCatalog catalog, final AirbyteMessage message) {
    throw new IllegalArgumentException(String.format(
        "Message contained record from a stream, %s, that was not in the catalog: %s",
        message.getRecord().getStream(),
        Jsons.serialize(catalog)));
  }

  @Override
  public void close(final boolean hasFailed) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot close; has not started.");
    Preconditions.checkState(!hasClosed, "Has already closed.");
    hasClosed = true;

    LOGGER.info("Started closing all connections");
    if (hasFailed) {
      LOGGER.error("Executing on failed close procedure");
    } else {
      LOGGER.info("Executing on success close procedure");
      bufferingStrategy.flushAll();
    }
    bufferingStrategy.close();

    if (lastFlushedState != null) {
      outputRecordCollector.accept(lastFlushedState);
    }
  }

}
