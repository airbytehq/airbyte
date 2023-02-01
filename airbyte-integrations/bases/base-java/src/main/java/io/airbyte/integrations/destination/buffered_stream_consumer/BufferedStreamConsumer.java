/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.functional.CheckedFunction;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.destination.dest_state_lifecycle_manager.DefaultDestStateLifecycleManager;
import io.airbyte.integrations.destination.dest_state_lifecycle_manager.DestStateLifecycleManager;
import io.airbyte.integrations.destination.record_buffer.BufferFlushType;
import io.airbyte.integrations.destination.record_buffer.BufferingStrategy;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.function.Consumer;
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
  private final Consumer<AirbyteMessage> outputRecordCollector;
  private final BufferingStrategy bufferingStrategy;
  private final DestStateLifecycleManager stateManager;

  private boolean hasStarted;
  private boolean hasClosed;

  public BufferedStreamConsumer(final Consumer<AirbyteMessage> outputRecordCollector,
                                final VoidCallable onStart,
                                final BufferingStrategy bufferingStrategy,
                                final CheckedConsumer<Boolean, Exception> onClose,
                                final ConfiguredAirbyteCatalog catalog,
                                final CheckedFunction<JsonNode, Boolean, Exception> isValidRecord) {
    this.outputRecordCollector = outputRecordCollector;
    this.hasStarted = false;
    this.hasClosed = false;
    this.onStart = onStart;
    this.onClose = onClose;
    this.catalog = catalog;
    this.streamNames = AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog);
    this.isValidRecord = isValidRecord;
    this.streamToIgnoredRecordCount = new HashMap<>();
    this.bufferingStrategy = bufferingStrategy;
    this.stateManager = new DefaultDestStateLifecycleManager();
  }

  @Override
  protected void startTracked() throws Exception {
    // todo (cgardens) - if we reuse this pattern, consider moving it into FailureTrackingConsumer.
    Preconditions.checkState(!hasStarted, "Consumer has already been started.");
    hasStarted = true;

    streamToIgnoredRecordCount.clear();
    LOGGER.info("{} started.", BufferedStreamConsumer.class);

    onStart.call();
  }

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
        if (BufferFlushType.FLUSH_ALL.equals(flushType.get())) {
          // when all buffers have been flushed then we can update all states as flushed
          markStatesAsFlushedToDestination();
        } else if (BufferFlushType.FLUSH_SINGLE_STREAM.equals(flushType.get())) {
          if (stateManager.supportsPerStreamFlush()) {
            // per-stream instance can handle flush of just a single stream
            markStatesAsFlushedToDestination();
          }
          /*
           * We don't mark {@link AirbyteStateMessage} as committed in the case with GLOBAL/LEGACY because
           * within a single stream being flushed it is not deterministic that all the AirbyteRecordMessages
           * have been committed
           */
        }
      }
      /*
       * TODO: (ryankfu) after record has added and time has been met then to see if time has elapsed then
       * flush the buffer
       *
       * The reason that this is where time component should exist here is primarily due to #acceptTracked
       * is the method that processes each AirbyteMessage. Method to call is
       * bufferingStrategy.flushWriter(stream, streamBuffer)
       */
    } else if (message.getType() == Type.STATE) {
      stateManager.addState(message);
    } else {
      LOGGER.warn("Unexpected message: " + message.getType());
    }
  }

  /**
   * After marking states as committed, emit the state message to platform then clear state messages
   * to avoid resending the same state message to the platform
   */
  private void markStatesAsFlushedToDestination() {
    stateManager.markPendingAsCommitted();
    stateManager.listCommitted().forEach(outputRecordCollector);
    stateManager.clearCommitted();
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
      bufferingStrategy.flushAll();
      markStatesAsFlushedToDestination();
    }
    bufferingStrategy.close();

    try {
      /*
       * TODO: (ryankfu) Remove usage of hasFailed with onClose after all destination connectors have been
       * updated to support checkpointing
       *
       * flushed is empty in 2 cases: 1. either it is full refresh (no state is emitted necessarily) 2. it
       * is stream but no states were flushed in both of these cases, if there was a failure, we should
       * not bother committing. otherwise attempt to commit
       */
      if (stateManager.listFlushed().isEmpty()) {
        onClose.accept(hasFailed);
      } else {
        /*
         * if any state message was flushed that means we should try to commit what we have. if
         * hasFailed=false, then it could be full success. if hasFailed=true, then going for partial
         * success.
         */
        onClose.accept(false);
      }

      stateManager.listCommitted().forEach(outputRecordCollector);
    } catch (final Exception e) {
      LOGGER.error("Close failed.", e);
      throw e;
    }
  }

}
