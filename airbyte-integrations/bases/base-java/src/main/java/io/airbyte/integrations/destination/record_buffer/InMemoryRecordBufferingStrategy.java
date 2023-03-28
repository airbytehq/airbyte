/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.integrations.destination.buffered_stream_consumer.CheckAndRemoveRecordWriter;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.integrations.destination.dest_state_lifecycle_manager.DefaultDestStateLifecycleManager;
import io.airbyte.integrations.destination.dest_state_lifecycle_manager.DestStateLifecycleManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Consumer;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is the default implementation of a {@link BufferStorage} to be backward compatible. Data is being buffered in a
 * {@link List<AirbyteRecordMessage>} as they are being consumed.
 * <p>
 * This should be deprecated as we slowly move towards using {@link SerializedBufferingStrategy} instead.
 */
public class InMemoryRecordBufferingStrategy implements BufferingStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(InMemoryRecordBufferingStrategy.class);
  private final Consumer<AirbyteMessage> outputRecordCollector;

  private Map<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>> streamBuffer = new HashMap<>();
  private final RecordWriter<AirbyteRecordMessage> recordWriter;
  private final CheckAndRemoveRecordWriter checkAndRemoveRecordWriter;
  private String fileName;

  private final RecordSizeEstimator recordSizeEstimator;
  private final DestStateLifecycleManager stateManager;
  private final long maxQueueSizeInBytes;
  private long bufferSizeInBytes;

  public InMemoryRecordBufferingStrategy(
      final RecordWriter<AirbyteRecordMessage> recordWriter,
      final long maxQueueSizeInBytes,
      final Consumer<AirbyteMessage> outputRecordCollector) {
    this(recordWriter, null, maxQueueSizeInBytes, outputRecordCollector);
  }

  public InMemoryRecordBufferingStrategy(
      final RecordWriter<AirbyteRecordMessage> recordWriter,
      final CheckAndRemoveRecordWriter checkAndRemoveRecordWriter,
      final long maxQueueSizeInBytes,
      final Consumer<AirbyteMessage> outputRecordCollector) {
    this.recordWriter = recordWriter;
    this.checkAndRemoveRecordWriter = checkAndRemoveRecordWriter;

    this.maxQueueSizeInBytes = maxQueueSizeInBytes;
    this.bufferSizeInBytes = 0;
    this.recordSizeEstimator = new RecordSizeEstimator();
    this.stateManager = new DefaultDestStateLifecycleManager();
    this.outputRecordCollector = outputRecordCollector;
  }

  @Override
  public Optional<BufferFlushType> addRecord(final AirbyteStreamNameNamespacePair stream, final AirbyteMessage message) throws Exception {
    Optional<BufferFlushType> flushed = Optional.empty();

    final long messageSizeInBytes = recordSizeEstimator.getEstimatedByteSize(message.getRecord());
    if (bufferSizeInBytes + messageSizeInBytes > maxQueueSizeInBytes) {
      flushAllStreams();
      flushed = Optional.of(BufferFlushType.FLUSH_ALL);
    }

    final List<AirbyteRecordMessage> bufferedRecords = streamBuffer.computeIfAbsent(stream, k -> new ArrayList<>());
    bufferedRecords.add(message.getRecord());
    bufferSizeInBytes += messageSizeInBytes;

    return flushed;
  }

  @Override
  public void flushSingleStream(final AirbyteStreamNameNamespacePair stream, final SerializableBuffer writer) throws Exception {
    LOGGER.info("Flushing single stream {}: {} records", stream.getName(), streamBuffer.get(stream).size());
    recordWriter.accept(stream, streamBuffer.get(stream));
    markStatesAsFlushedToDestination();
    LOGGER.info("Flushing completed for {}", stream.getName());
  }

  @Override
  public void flushAllStreams() throws Exception {
    for (final Map.Entry<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>> entry : streamBuffer.entrySet()) {
      LOGGER.info("Flushing {}: {} records ({})", entry.getKey().getName(), entry.getValue().size(),
          FileUtils.byteCountToDisplaySize(bufferSizeInBytes));
      recordWriter.accept(entry.getKey(), entry.getValue());
      if (checkAndRemoveRecordWriter != null) {
        fileName = checkAndRemoveRecordWriter.apply(entry.getKey(), fileName);
      }
      LOGGER.info("Flushing completed for {}", entry.getKey().getName());
    }
    markStatesAsFlushedToDestination();
    clear();
    bufferSizeInBytes = 0;
  }

  /**
   * After marking states as committed, return the state message to platform then clear state messages to avoid resending the same state message to
   * the platform. Also updates the next time a buffer flush should occur since it is deterministic that when this method is called all data has been
   * successfully committed to destination
   */
  private void markStatesAsFlushedToDestination() {
    stateManager.markPendingAsCommitted();
    stateManager.listCommitted().forEach(outputRecordCollector);
    stateManager.clearCommitted();
  }

  @Override
  public void clear() {
    streamBuffer = new HashMap<>();
  }

  @Override
  public void addStateMessage(final AirbyteMessage message) {
    stateManager.addState(message);
  }

  @Override
  public void close() throws Exception {}

}
