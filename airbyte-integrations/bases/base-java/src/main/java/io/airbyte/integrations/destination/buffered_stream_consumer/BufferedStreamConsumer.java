/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.bytes.ByteUtils;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class consumes AirbyteMessages from the worker.
 *
 * <p>
 * Record Messages: It adds record messages to a buffer. Under 2 conditions, it will flush the
 * records in the buffer to a temporary table in the destination. Condition 1: The buffer fills up
 * (the buffer is designed to be small enough as not to exceed the memory of the container).
 * Condition 2: On close.
 * </p>
 *
 * <p>
 * State Messages: This consumer tracks the last state message it has accepted. It also tracks the
 * last state message that was committed to the temporary table. For now, we only emit a message if
 * everything is successful. Once checkpointing is turned on, we will emit the state message as long
 * as the onClose successfully commits any messages to the raw table.
 * </p>
 *
 * <p>
 * All other message types are ignored.
 * </p>
 *
 * <p>
 * Throughout the lifecycle of the consumer, messages get promoted from buffered to flushed to
 * committed. A record message when it is received is immediately buffered. When the buffer fills
 * up, all buffered records are flushed out of memory using the user-provided recordWriter. When
 * this flush happens, a state message is moved from pending to flushed. On close, if the
 * user-provided onClose function is successful, then the flushed state record is considered
 * committed and is then emitted. We expect this class to only ever emit either 1 state message (in
 * the case of a full or partial success) or 0 state messages (in the case where the onClose step
 * was never reached or did not complete without exception).
 * </p>
 *
 * <p>
 * When a record is "flushed" it is moved from the docker container to the destination. By
 * convention, it is usually placed in some sort of temporary storage on the destination (e.g. a
 * temporary database or file store). The logic in close handles committing the temporary
 * representation data to the final store (e.g. final table). In the case of Copy destinations they
 * often have additional temporary stores. The common pattern for copy destination is that flush
 * pushes the data into cloud storage and then close copies from cloud storage to a temporary table
 * AND then copies from the temporary table into the final table. This abstraction is blind to that
 * detail as it implementation detail of how copy destinations implement close.
 * </p>
 */
public class BufferedStreamConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferedStreamConsumer.class);

  private final VoidCallable onStart;
  private final RecordWriter recordWriter;
  private final CheckedConsumer<Boolean, Exception> onClose;
  private final Set<AirbyteStreamNameNamespacePair> streamNames;
  private final List<AirbyteMessage> buffer;
  private final ConfiguredAirbyteCatalog catalog;
  private final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord;
  private final Map<AirbyteStreamNameNamespacePair, Long> pairToIgnoredRecordCount;
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final long maxQueueSizeInBytes;
  private long bufferSizeInBytes;

  private boolean hasStarted;
  private boolean hasClosed;

  private AirbyteMessage lastFlushedState;
  private AirbyteMessage pendingState;

  public BufferedStreamConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
                                final VoidCallable onStart,
                                final RecordWriter recordWriter,
                                final CheckedConsumer<Boolean, Exception> onClose,
                                final ConfiguredAirbyteCatalog catalog,
                                final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord,
                                final long maxQueueSizeInBytes) {
    this.outputRecordCollector = outputRecordCollector;
    this.maxQueueSizeInBytes = maxQueueSizeInBytes;
    this.hasStarted = false;
    this.hasClosed = false;
    this.onStart = onStart;
    this.recordWriter = recordWriter;
    this.onClose = onClose;
    this.catalog = catalog;
    this.streamNames = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);
    this.isValidRecord = isValidRecord;
    this.buffer = new ArrayList<>(10_000);
    this.bufferSizeInBytes = 0;
    this.pairToIgnoredRecordCount = new HashMap<>();
  }

  @Override
  protected void startTracked() throws Exception {
    // todo (cgardens) - if we reuse this pattern, consider moving it into FailureTrackingConsumer.
    Preconditions.checkState(!hasStarted, "Consumer has already been started.");
    hasStarted = true;

    pairToIgnoredRecordCount.clear();
    LOGGER.info("{} started.", BufferedStreamConsumer.class);

    onStart.call();
  }

  @Override
  protected void acceptTracked(final AirbyteMessage message) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started");
    if (message.getType() == Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();
      final AirbyteStreamNameNamespacePair stream = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);

      if (!streamNames.contains(stream)) {
        throwUnrecognizedStream(catalog, message);
      }

      if (!isValidRecord.apply(message.getRecord().getData())) {
        pairToIgnoredRecordCount.put(stream, pairToIgnoredRecordCount.getOrDefault(stream, 0L) + 1L);
        return;
      }

      // TODO use a more efficient way to compute bytes that doesn't require double serialization (records
      // are serialized again when writing to
      // the destination
      long messageSizeInBytes = ByteUtils.getSizeInBytesForUTF8CharSet(Jsons.serialize(recordMessage.getData()));
      if (bufferSizeInBytes + messageSizeInBytes >= maxQueueSizeInBytes) {
        LOGGER.info("Flushing buffer...");
        flushQueueToDestination();
        bufferSizeInBytes = 0;
      }

      buffer.add(message);
      bufferSizeInBytes += messageSizeInBytes;

    } else if (message.getType() == Type.STATE) {
      pendingState = message;
    } else {
      LOGGER.warn("Unexpected message: " + message.getType());
    }

  }

  private void flushQueueToDestination() throws Exception {
    final Map<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>> recordsByStream = buffer.stream()
        .map(AirbyteMessage::getRecord)
        .collect(Collectors.groupingBy(AirbyteStreamNameNamespacePair::fromRecordMessage));

    buffer.clear();

    for (final Map.Entry<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>> entry : recordsByStream.entrySet()) {
      recordWriter.accept(entry.getKey(), entry.getValue());
    }

    if (pendingState != null) {
      lastFlushedState = pendingState;
      pendingState = null;
    }
  }

  private void throwUnrecognizedStream(final ConfiguredAirbyteCatalog catalog, final AirbyteMessage message) {
    throw new IllegalArgumentException(
        String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
            Jsons.serialize(catalog), Jsons.serialize(message)));
  }

  @Override
  protected void close(final boolean hasFailed) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot close; has not started.");
    Preconditions.checkState(!hasClosed, "Has already closed.");
    hasClosed = true;

    pairToIgnoredRecordCount
        .forEach((pair, count) -> LOGGER.warn("A total of {} record(s) of data from stream {} were invalid and were ignored.", count, pair));
    if (hasFailed) {
      LOGGER.error("executing on failed close procedure.");
    } else {
      LOGGER.info("executing on success close procedure.");
      flushQueueToDestination();
    }

    try {
      // if no state was emitted (i.e. full refresh), if there were still no failures, then we can
      // still succeed.
      if (lastFlushedState == null) {
        onClose.accept(hasFailed);
      } else {
        // if any state message flushed that means we can still go for at least a partial success.
        onClose.accept(false);
      }

      // if onClose succeeds without exception then we can emit the state record because it means its
      // records were not only flushed, but committed.
      if (lastFlushedState != null) {
        outputRecordCollector.accept(lastFlushedState);
      }
    } catch (final Exception e) {
      LOGGER.error("Close failed.", e);
      throw e;
    }
  }

}
