/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.integrations.destination.buffered_stream_consumer.CheckAndRemoveRecordWriter;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordSizeEstimator;
import io.airbyte.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is the default implementation of a {@link BufferStorage} to be backward compatible. Data is
 * being buffered in a {@link List<AirbyteRecordMessage>} as they are being consumed.
 *
 * This should be deprecated as we slowly move towards using {@link SerializedBufferingStrategy}
 * instead.
 */
public class InMemoryRecordBufferingStrategy implements BufferingStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(InMemoryRecordBufferingStrategy.class);

  private Map<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>> streamBuffer = new HashMap<>();
  private final RecordWriter<AirbyteRecordMessage> recordWriter;
  private final CheckAndRemoveRecordWriter checkAndRemoveRecordWriter;
  private String fileName;

  private final RecordSizeEstimator recordSizeEstimator;
  private final long maxQueueSizeInBytes;
  private long bufferSizeInBytes;

  public InMemoryRecordBufferingStrategy(final RecordWriter<AirbyteRecordMessage> recordWriter,
                                         final long maxQueueSizeInBytes) {
    this(recordWriter, null, maxQueueSizeInBytes);
  }

  public InMemoryRecordBufferingStrategy(final RecordWriter<AirbyteRecordMessage> recordWriter,
                                         final CheckAndRemoveRecordWriter checkAndRemoveRecordWriter,
                                         final long maxQueueSizeInBytes) {
    this.recordWriter = recordWriter;
    this.checkAndRemoveRecordWriter = checkAndRemoveRecordWriter;

    this.maxQueueSizeInBytes = maxQueueSizeInBytes;
    this.bufferSizeInBytes = 0;
    this.recordSizeEstimator = new RecordSizeEstimator();
  }

  @Override
  public Optional<BufferFlushType> addRecord(final AirbyteStreamNameNamespacePair stream, final AirbyteMessage message) throws Exception {
    Optional<BufferFlushType> flushed = Optional.empty();

    final long messageSizeInBytes = recordSizeEstimator.getEstimatedByteSize(message.getRecord());
    if (bufferSizeInBytes + messageSizeInBytes > maxQueueSizeInBytes) {
      flushAll();
      flushed = Optional.of(BufferFlushType.FLUSH_ALL);
      bufferSizeInBytes = 0;
    }

    final List<AirbyteRecordMessage> bufferedRecords = streamBuffer.computeIfAbsent(stream, k -> new ArrayList<>());
    bufferedRecords.add(message.getRecord());
    bufferSizeInBytes += messageSizeInBytes;

    return flushed;
  }

  @Override
  public void flushWriter(final AirbyteStreamNameNamespacePair stream, final SerializableBuffer writer) throws Exception {
    LOGGER.info("Flushing single stream {}: {} records", stream, streamBuffer.get(stream).size());
    recordWriter.accept(stream, streamBuffer.get(stream));
  }

  @Override
  public void flushAll() throws Exception {
    for (final Map.Entry<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>> entry : streamBuffer.entrySet()) {
      LOGGER.info("Flushing {}: {} records ({})", entry.getKey().getName(), entry.getValue().size(),
          FileUtils.byteCountToDisplaySize(bufferSizeInBytes));
      recordWriter.accept(entry.getKey(), entry.getValue());
      if (checkAndRemoveRecordWriter != null) {
        fileName = checkAndRemoveRecordWriter.apply(entry.getKey(), fileName);
      }
    }
    close();
    clear();
  }

  @Override
  public void clear() {
    streamBuffer = new HashMap<>();
  }

  @Override
  public void close() throws Exception {}

}
