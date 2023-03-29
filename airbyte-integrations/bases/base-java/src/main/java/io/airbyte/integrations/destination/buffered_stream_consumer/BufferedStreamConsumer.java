/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Preconditions;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.record_buffer.BufferFlushType;
import io.airbyte.integrations.destination.record_buffer.BufferingStrategy;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Duration;
import java.time.Instant;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
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
 * up, all buffered records are flushed out of memory using the user-provided recordBuffer. When
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
 * representation data to the final store (e.g. final table). In the case of staging destinations
 * they often have additional temporary stores. The common pattern for staging destination is that
 * flush pushes the data into a staging area in cloud storage and then close copies from staging to
 * a temporary table AND then copies from the temporary table into the final table. This abstraction
 * is blind to the detail of how staging destinations implement their close.
 * </p>
 */
public class BufferedStreamConsumer extends FailureTrackingAirbyteMessageConsumer implements AirbyteMessageConsumer {

  private static final Logger LOGGER = LoggerFactory.getLogger(BufferedStreamConsumer.class);

  private final VoidCallable onStart;
  private final CheckedConsumer<Boolean, Exception> onClose;
  private final Set<AirbyteStreamNameNamespacePair> streamNames;
  private final ConfiguredAirbyteCatalog catalog;
  private final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord;
  private final Map<AirbyteStreamNameNamespacePair, Long> streamToIgnoredRecordCount;
  private final BufferingStrategy bufferingStrategy;

  private boolean hasStarted;
  private boolean hasClosed;

  private Instant nextFlushDeadline;
  private final Duration bufferFlushFrequency;

  public BufferedStreamConsumer(final VoidCallable onStart,
                                final BufferingStrategy bufferingStrategy,
                                final CheckedConsumer<Boolean, Exception> onClose,
                                final ConfiguredAirbyteCatalog catalog,
                                final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord) {
    this(onStart,
        bufferingStrategy,
        onClose,
        catalog,
        isValidRecord,
        Duration.ofMinutes(15));
  }

  /*
   * NOTE: this is only used for testing purposes, future work would be re-visit if #acceptTracked
   * should take in an Instant parameter which would require refactoring all MessageConsumers
   */
  @VisibleForTesting
  BufferedStreamConsumer(final VoidCallable onStart,
                         final BufferingStrategy bufferingStrategy,
                         final CheckedConsumer<Boolean, Exception> onClose,
                         final ConfiguredAirbyteCatalog catalog,
                         final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord,
                         final Duration flushFrequency) {
    this.hasStarted = false;
    this.hasClosed = false;
    this.onStart = onStart;
    this.onClose = onClose;
    this.catalog = catalog;
    this.streamNames = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);
    this.isValidRecord = isValidRecord;
    this.streamToIgnoredRecordCount = new HashMap<>();
    this.bufferingStrategy = bufferingStrategy;
    this.bufferFlushFrequency = flushFrequency;
  }

  @Override
  protected void startTracked() throws Exception {
    // todo (cgardens) - if we reuse this pattern, consider moving it into FailureTrackingConsumer.
    Preconditions.checkState(!hasStarted, "Consumer has already been started.");
    hasStarted = true;
    resetFlushDeadline();
    streamToIgnoredRecordCount.clear();
    LOGGER.info("{} started.", BufferedStreamConsumer.class);
    onStart.call();
  }

  /**
   * AcceptTracked will still process AirbyteMessages as usual with the addition of periodically
   * flushing buffer and writing data to destination storage
   *
   * @param message {@link AirbyteMessage} to be processed
   * @throws Exception
   */
  @Override
  protected void acceptTracked(final AirbyteMessage message) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started");
    if (message.getType() == Type.RECORD) {
      final AirbyteRecordMessage recordMessage = message.getRecord();
      final AirbyteStreamNameNamespacePair stream = AirbyteStreamNameNamespacePair.fromRecordMessage(recordMessage);

      // if stream is not part of list of streams to sync to then throw invalid stream exception
      if (!streamNames.contains(stream)) {
        throwUnrecognizedStream(catalog, message);
      }

      if (!isValidRecord.apply(message.getRecord().getData())) {
        streamToIgnoredRecordCount.put(stream, streamToIgnoredRecordCount.getOrDefault(stream, 0L) + 1L);
        return;
      }

      final Optional<BufferFlushType> flushType = bufferingStrategy.addRecord(stream, message);
      // if present means that a flush occurred
      if (flushType.isPresent()) {
        // this resets the time based flushing behavior
        resetFlushDeadline();
      }
    } else if (message.getType() == Type.STATE) {
      bufferingStrategy.addStateMessage(message);
    } else {
      LOGGER.warn("Unexpected message: " + message.getType());
    }
    periodicBufferFlush();
  }

  /**
   * Updates the next time a buffer flush should occur since it is deterministic that when this method
   * is called all data has been scheduled to flush to the destination
   */
  private void resetFlushDeadline() {
    nextFlushDeadline = Instant.now().plus(bufferFlushFrequency);
  }

  /**
   * Periodically flushes buffered data to destination storage when exceeding flush deadline. Also
   * resets the last time a flush occurred
   */
  private void periodicBufferFlush() throws Exception {
    // When the last time the buffered has been flushed exceed the frequency, flush the current
    // buffer before receiving incoming AirbyteMessage
    if (Instant.now().isAfter(nextFlushDeadline)) {
      LOGGER.info("Periodic buffer flush started");
      try {
        bufferingStrategy.flushAllStreams();
        resetFlushDeadline();
      } catch (final Exception e) {
        LOGGER.error("Periodic buffer flush failed", e);
        throw e;
      }
    }
  }

  private static void throwUnrecognizedStream(final ConfiguredAirbyteCatalog catalog, final AirbyteMessage message) {
    throw new IllegalArgumentException(
        String.format("Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
            Jsons.serialize(catalog), Jsons.serialize(message)));
  }

  /**
   * Cleans up buffer based on whether the sync was successful or some exception occurred. In the case
   * where a failure occurred we do a simple clean up any lingering data. Otherwise, flush any
   * remaining data that has been stored. This is fine even if the state has not been received since
   * this Airbyte promises at least once delivery
   *
   * @param hasFailed true if the stream replication failed partway through, false otherwise
   * @throws Exception
   */
  @Override
  protected void close(final boolean hasFailed) throws Exception {
    Preconditions.checkState(hasStarted, "Cannot close; has not started.");
    Preconditions.checkState(!hasClosed, "Has already closed.");
    hasClosed = true;

    streamToIgnoredRecordCount
        .forEach((pair, count) -> LOGGER.warn("A total of {} record(s) of data from stream {} were invalid and were ignored.", count, pair));
    if (hasFailed) {
      LOGGER.error("executing on failed close procedure.");
    } else {
      LOGGER.info("executing on success close procedure.");
      // When flushing the buffer, this will call the respective #flushBufferFunction which bundles
      // the flush and commit operation, so if successful then mark state as committed
      bufferingStrategy.flushAllStreams();
      resetFlushDeadline();
    }
    bufferingStrategy.close();

    try {
      onClose.accept(hasFailed);
    } catch (final Exception e) {
      LOGGER.error("Close failed.", e);
      throw e;
    }
  }

}
