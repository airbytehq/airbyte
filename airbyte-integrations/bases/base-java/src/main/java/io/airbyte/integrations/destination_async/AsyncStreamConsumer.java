/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination_async.buffers.BufferEnqueue;
import io.airbyte.integrations.destination_async.buffers.BufferManager;
import io.airbyte.integrations.destination_async.state.FlushFailure;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Set;
import java.util.function.Consumer;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Async version of the
 * {@link io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer}.
 * <p>
 * With this consumer, a destination is able to continue reading records until hitting the maximum
 * memory limit governed by {@link GlobalMemoryManager}. Record writing is decoupled via
 * {@link FlushWorkers}. See the other linked class for more detail.
 */
@Slf4j
public class AsyncStreamConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(AsyncStreamConsumer.class);

  private final OnStartFunction onStart;
  private final OnCloseFunction onClose;
  private final ConfiguredAirbyteCatalog catalog;
  private final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord;
  private final BufferManager bufferManager;
  private final BufferEnqueue bufferEnqueue;
  private final FlushWorkers flushWorkers;
  private final Set<StreamDescriptor> streamNames;
  private final IgnoredRecordsTracker ignoredRecordsTracker;
  private final FlushFailure flushFailure;

  private boolean hasStarted;
  private boolean hasClosed;

  public AsyncStreamConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
                             final OnStartFunction onStart,
                             final OnCloseFunction onClose,
                             final DestinationFlushFunction flusher,
                             final ConfiguredAirbyteCatalog catalog,
                             final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord,
                             final BufferManager bufferManager) {
    this(outputRecordCollector, onStart, onClose, flusher, catalog, isValidRecord, bufferManager, new FlushFailure());
  }

  @VisibleForTesting
  public AsyncStreamConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
                             final OnStartFunction onStart,
                             final OnCloseFunction onClose,
                             final DestinationFlushFunction flusher,
                             final ConfiguredAirbyteCatalog catalog,
                             final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord,
                             final BufferManager bufferManager,
                             final FlushFailure flushFailure) {
    hasStarted = false;
    hasClosed = false;

    this.onStart = onStart;
    this.onClose = onClose;
    this.catalog = catalog;
    this.isValidRecord = isValidRecord;
    this.bufferManager = bufferManager;
    bufferEnqueue = bufferManager.getBufferEnqueue();
    this.flushFailure = flushFailure;
    flushWorkers = new FlushWorkers(bufferManager.getBufferDequeue(), flusher, outputRecordCollector, flushFailure);
    streamNames = StreamDescriptorUtils.fromConfiguredCatalog(catalog);
    ignoredRecordsTracker = new IgnoredRecordsTracker();
  }

  @Override
  public void start() throws Exception {
    Preconditions.checkState(!hasStarted, "Consumer has already been started.");
    hasStarted = true;

    flushWorkers.start();

    LOGGER.info("{} started.", AsyncStreamConsumer.class);
    onStart.call();
  }

  @Override
  public void accept(final AirbyteMessage message) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started");
    propagateFlushWorkerExceptionIfPresent();
    /*
     * intentionally putting extractStream outside the buffer manager so that if in the future we want
     * to try to use a thread pool to partially deserialize to get record type and stream name, we can
     * do it without touching buffer manager.
     */

    if (message.getType() == Type.RECORD) {
      validateRecord(message);
    }

    bufferEnqueue.addRecord(message);
  }

  @Override
  public void close() throws Exception {
    Preconditions.checkState(hasStarted, "Cannot close; has not started.");
    Preconditions.checkState(!hasClosed, "Has already closed.");
    hasClosed = true;

    // assume closing upload workers will flush all accepted records.
    // we need to close the workers before closing the bufferManagers (and underlying buffers)
    // or we risk in-memory data.
    flushWorkers.close();

    bufferManager.close();
    ignoredRecordsTracker.report();
    onClose.call();

    // as this throws an exception, we need to be after all other close functions.
    propagateFlushWorkerExceptionIfPresent();
    LOGGER.info("{} closed.", AsyncStreamConsumer.class);
  }

  private void propagateFlushWorkerExceptionIfPresent() throws Exception {
    if (flushFailure.isFailed()) {
      throw flushFailure.getException();
    }
  }

  private void validateRecord(final AirbyteMessage message) {
    final StreamDescriptor streamDescriptor = new StreamDescriptor()
        .withNamespace(message.getRecord().getNamespace())
        .withName(message.getRecord().getStream());
    // if stream is not part of list of streams to sync to then throw invalid stream exception
    if (!streamNames.contains(streamDescriptor)) {
      throwUnrecognizedStream(catalog, message);
    }

    trackIsValidRecord(message, streamDescriptor);
  }

  private void trackIsValidRecord(final AirbyteMessage message, final StreamDescriptor streamDescriptor) {
    // todo (cgardens) - is valid should also move inside the tracker.
    try {

      if (!isValidRecord.apply(message.getRecord().getData())) {
        ignoredRecordsTracker.addRecord(streamDescriptor);
      }
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private static void throwUnrecognizedStream(final ConfiguredAirbyteCatalog catalog, final AirbyteMessage message) {
    throw new IllegalArgumentException(
        String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
            Jsons.serialize(catalog), Jsons.serialize(message)));
  }

}
