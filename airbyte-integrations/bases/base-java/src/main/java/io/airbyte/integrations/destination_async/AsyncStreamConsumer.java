/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination_async.buffers.BufferEnqueue;
import io.airbyte.integrations.destination_async.buffers.BufferManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Optional;
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

  private static final String NON_STREAM_STATE_IDENTIFIER = "GLOBAL";
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final OnStartFunction onStart;
  private final OnCloseFunction onClose;
  private final ConfiguredAirbyteCatalog catalog;
  private final BufferManager bufferManager;
  private final BufferEnqueue bufferEnqueue;
  private final FlushWorkers flushWorkers;
  private final Set<StreamDescriptor> streamNames;

  private boolean hasStarted;
  private boolean hasClosed;

  public AsyncStreamConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
                             final OnStartFunction onStart,
                             final OnCloseFunction onClose,
                             final DestinationFlushFunction flusher,
                             final ConfiguredAirbyteCatalog catalog,
                             final BufferManager bufferManager) {
    hasStarted = false;
    hasClosed = false;

    this.outputRecordCollector = outputRecordCollector;
    this.onStart = onStart;
    this.onClose = onClose;
    this.catalog = catalog;
    this.bufferManager = bufferManager;
    bufferEnqueue = bufferManager.getBufferEnqueue();
    flushWorkers = new FlushWorkers(this.bufferManager.getBufferDequeue(), flusher);
    streamNames = StreamDescriptorUtils.fromConfiguredCatalog(catalog);
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
    /*
     * intentionally putting extractStream outside the buffer manager so that if in the future we want
     * to try to use a threadpool to partial deserialize to get record type and stream name, we can do
     * it without touching buffer manager.
     */
    extractStream(message)
        .ifPresent(streamDescriptor -> bufferEnqueue.addRecord(streamDescriptor, message));
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
    onClose.call();
    LOGGER.info("{} closed.", AsyncStreamConsumer.class);
  }

  // todo (cgardens) - handle global state.
  /**
   * Extract the stream from the message, if the message is a record or state. Otherwise, we don't
   * care.
   *
   * @param message message to extract stream from
   * @return stream descriptor if the message is a record or state, otherwise empty. In the case of
   *         global state messages the stream descriptor is hardcoded
   */
  private Optional<StreamDescriptor> extractStream(final AirbyteMessage message) {
    if (message.getType() == Type.RECORD) {
      final StreamDescriptor streamDescriptor = new StreamDescriptor()
          .withNamespace(message.getRecord().getNamespace())
          .withName(message.getRecord().getStream());

      validateRecord(message, streamDescriptor);

      return Optional.of(streamDescriptor);
    } else if (message.getType() == Type.STATE) {
      if (message.getState().getType() == AirbyteStateType.STREAM) {
        return Optional.of(message.getState().getStream().getStreamDescriptor());
      } else {
        return Optional.of(new StreamDescriptor().withNamespace(NON_STREAM_STATE_IDENTIFIER).withNamespace(NON_STREAM_STATE_IDENTIFIER));
      }
    } else {
      return Optional.empty();
    }
  }

  private void validateRecord(final AirbyteMessage message, final StreamDescriptor streamDescriptor) {
    // if stream is not part of list of streams to sync to then throw invalid stream exception
    if (!streamNames.contains(streamDescriptor)) {
      throwUnrecognizedStream(catalog, message);
    }
  }

  private static void throwUnrecognizedStream(final ConfiguredAirbyteCatalog catalog, final AirbyteMessage message) {
    throw new IllegalArgumentException(
        String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
            Jsons.serialize(catalog), Jsons.serialize(message)));
  }

}
