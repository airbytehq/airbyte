/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async;

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.SerializedAirbyteMessageConsumer;
import io.airbyte.integrations.destination.buffered_stream_consumer.OnStartFunction;
import io.airbyte.integrations.destination_async.buffers.BufferEnqueue;
import io.airbyte.integrations.destination_async.buffers.BufferManager;
import io.airbyte.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.integrations.destination_async.state.FlushFailure;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
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
public class AsyncStreamConsumer implements SerializedAirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(AsyncStreamConsumer.class);

  private final OnStartFunction onStart;
  private final OnCloseFunction onClose;
  private final ConfiguredAirbyteCatalog catalog;
  private final BufferManager bufferManager;
  private final BufferEnqueue bufferEnqueue;
  private final FlushWorkers flushWorkers;
  private final Set<StreamDescriptor> streamNames;
  private final FlushFailure flushFailure;

  private boolean hasStarted;
  private boolean hasClosed;
  // This is to account for the references when deserialization to a PartialAirbyteMessage. The
  // calculation is as follows:
  // PartialAirbyteMessage (4) + Max( PartialRecordMessage(4), PartialStateMessage(6)) with
  // PartialStateMessage being larger with more nested objects within it. Using 8 bytes as we assumed
  // a 64 bit JVM.
  final int PARTIAL_DESERIALIZE_REF_BYTES = 10 * 8;

  public AsyncStreamConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
                             final OnStartFunction onStart,
                             final OnCloseFunction onClose,
                             final DestinationFlushFunction flusher,
                             final ConfiguredAirbyteCatalog catalog,
                             final BufferManager bufferManager) {
    this(outputRecordCollector, onStart, onClose, flusher, catalog, bufferManager, new FlushFailure());
  }

  @VisibleForTesting
  public AsyncStreamConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
                             final OnStartFunction onStart,
                             final OnCloseFunction onClose,
                             final DestinationFlushFunction flusher,
                             final ConfiguredAirbyteCatalog catalog,
                             final BufferManager bufferManager,
                             final FlushFailure flushFailure) {
    hasStarted = false;
    hasClosed = false;

    this.onStart = onStart;
    this.onClose = onClose;
    this.catalog = catalog;
    this.bufferManager = bufferManager;
    bufferEnqueue = bufferManager.getBufferEnqueue();
    this.flushFailure = flushFailure;
    flushWorkers = new FlushWorkers(bufferManager.getBufferDequeue(), flusher, outputRecordCollector, flushFailure, bufferManager.getStateManager());
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
  public void accept(final String messageString, final Integer sizeInBytes) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started");
    propagateFlushWorkerExceptionIfPresent();
    /*
     * intentionally putting extractStream outside the buffer manager so that if in the future we want
     * to try to use a thread pool to partially deserialize to get record type and stream name, we can
     * do it without touching buffer manager.
     */
    deserializeAirbyteMessage(messageString)
        .ifPresent(message -> {
          if (Type.RECORD.equals(message.getType())) {
            validateRecord(message);
          }
          bufferEnqueue.addRecord(message, sizeInBytes + PARTIAL_DESERIALIZE_REF_BYTES);
        });
  }

  /**
   * Deserializes to a {@link PartialAirbyteMessage} which can represent both a Record or a State
   * Message
   *
   * PartialAirbyteMessage holds either:
   * <li>entire serialized message string when message is a valid State Message
   * <li>serialized AirbyteRecordMessage when message is a valid Record Message</li>
   *
   * @param messageString the string to deserialize
   * @return PartialAirbyteMessage if the message is valid, empty otherwise
   */
  @VisibleForTesting
  public static Optional<PartialAirbyteMessage> deserializeAirbyteMessage(final String messageString) {
    // TODO: (ryankfu) plumb in the serialized AirbyteStateMessage to match AirbyteRecordMessage code
    // parity. https://github.com/airbytehq/airbyte/issues/27530 for additional context
    final Optional<PartialAirbyteMessage> messageOptional = Jsons.tryDeserialize(messageString, PartialAirbyteMessage.class)
        .map(partial -> {
          if (Type.RECORD.equals(partial.getType()) && partial.getRecord().getData() != null) {
            return partial.withSerialized(partial.getRecord().getData().toString());
          } else if (Type.STATE.equals(partial.getType())) {
            return partial.withSerialized(messageString);
          } else {
            return null;
          }
        });

    if (messageOptional.isPresent()) {
      return messageOptional;
    }
    throw new RuntimeException(String.format("Invalid serialized message: %s", messageString));
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

    // as this throws an exception, we need to be after all other close functions.
    propagateFlushWorkerExceptionIfPresent();
    LOGGER.info("{} closed", AsyncStreamConsumer.class);
  }

  private void propagateFlushWorkerExceptionIfPresent() throws Exception {
    if (flushFailure.isFailed()) {
      throw flushFailure.getException();
    }
  }

  private void validateRecord(final PartialAirbyteMessage message) {
    final StreamDescriptor streamDescriptor = new StreamDescriptor()
        .withNamespace(message.getRecord().getNamespace())
        .withName(message.getRecord().getStream());
    // if stream is not part of list of streams to sync to then throw invalid stream exception
    if (!streamNames.contains(streamDescriptor)) {
      throwUnrecognizedStream(catalog, message);
    }
  }

  private static void throwUnrecognizedStream(final ConfiguredAirbyteCatalog catalog, final PartialAirbyteMessage message) {
    throw new IllegalArgumentException(
        String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
            Jsons.serialize(catalog), Jsons.serialize(message)));
  }

}
