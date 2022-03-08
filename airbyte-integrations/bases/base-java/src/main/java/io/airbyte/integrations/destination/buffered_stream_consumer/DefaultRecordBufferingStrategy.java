/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultRecordBufferingStrategy implements RecordBufferingStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultRecordBufferingStrategy.class);

  private Map<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>> streamBuffer = new HashMap<>();
  private final RecordWriter<AirbyteRecordMessage> recordWriter;
  private final CheckAndRemoveRecordWriter checkAndRemoveRecordWriter;
  private String fileName;

  private final RecordSizeEstimator recordSizeEstimator;
  private final long maxQueueSizeInBytes;
  private long bufferSizeInBytes;
  private VoidCallable onFlushEventHook;

  public DefaultRecordBufferingStrategy(final RecordWriter<AirbyteRecordMessage> recordWriter,
                                        final long maxQueueSizeInBytes) {
    this(recordWriter, null, maxQueueSizeInBytes);
  }

  public DefaultRecordBufferingStrategy(final RecordWriter<AirbyteRecordMessage> recordWriter,
                                        final CheckAndRemoveRecordWriter checkAndRemoveRecordWriter,
                                        final long maxQueueSizeInBytes) {
    this.recordWriter = recordWriter;
    this.checkAndRemoveRecordWriter = checkAndRemoveRecordWriter;

    this.maxQueueSizeInBytes = maxQueueSizeInBytes;
    this.bufferSizeInBytes = 0;
    this.recordSizeEstimator = new RecordSizeEstimator();
    this.onFlushEventHook = null;
  }

  @Override
  public void addRecord(AirbyteStreamNameNamespacePair stream, AirbyteMessage message) throws Exception {
    final long messageSizeInBytes = recordSizeEstimator.getEstimatedByteSize(message.getRecord());
    if (bufferSizeInBytes + messageSizeInBytes > maxQueueSizeInBytes) {
      flushAll();
      bufferSizeInBytes = 0;
    }

    final List<AirbyteRecordMessage> bufferedRecords = streamBuffer.computeIfAbsent(stream, k -> new ArrayList<>());
    bufferedRecords.add(message.getRecord());
    bufferSizeInBytes += messageSizeInBytes;
  }

  @Override
  public void flushWriter(AirbyteStreamNameNamespacePair stream, RecordBufferImplementation writer) throws Exception {
    LOGGER.info("Flushing single stream {}: {} records", stream, streamBuffer.get(stream).size());
    recordWriter.accept(stream, streamBuffer.get(stream));
  }

  @Override
  public void flushAll() throws Exception {
    AirbyteSentry.executeWithTracing("FlushBuffer", () -> {
      for (final Map.Entry<AirbyteStreamNameNamespacePair, List<AirbyteRecordMessage>> entry : streamBuffer.entrySet()) {
        LOGGER.info("Flushing {}: {} records", entry.getKey().getName(), entry.getValue().size());
        recordWriter.accept(entry.getKey(), entry.getValue());
        if (checkAndRemoveRecordWriter != null) {
          fileName = checkAndRemoveRecordWriter.apply(entry.getKey(), fileName);
        }
      }
    }, Map.of("bufferSizeInBytes", bufferSizeInBytes));
    clear();

    if (onFlushEventHook != null) {
      onFlushEventHook.call();
    }
  }

  @Override
  public void clear() {
    streamBuffer = new HashMap<>();
  }

  @Override
  public void registerFlushEventHook(final VoidCallable onFlushEventHook) {
    this.onFlushEventHook = onFlushEventHook;
  }

  @Override
  public void close() throws Exception {}

}
