/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.integrations.base.sentry.AirbyteSentry;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SerializedBufferingStrategy implements BufferingStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(SerializedBufferingStrategy.class);

  private final CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> onCreateBuffer;
  private final CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> onStreamFlush;
  private VoidCallable onFlushAllEventHook;

  private Map<AirbyteStreamNameNamespacePair, SerializableBuffer> allBuffers = new HashMap<>();
  private long totalBufferSizeInBytes;
  private final ConfiguredAirbyteCatalog catalog;

  public SerializedBufferingStrategy(final CheckedBiFunction<AirbyteStreamNameNamespacePair, ConfiguredAirbyteCatalog, SerializableBuffer, Exception> onCreateBuffer,
                                     final ConfiguredAirbyteCatalog catalog,
                                     final CheckedBiConsumer<AirbyteStreamNameNamespacePair, SerializableBuffer, Exception> onStreamFlush) {
    this.onCreateBuffer = onCreateBuffer;
    this.catalog = catalog;
    this.onStreamFlush = onStreamFlush;
    this.totalBufferSizeInBytes = 0;
    this.onFlushAllEventHook = null;
  }

  @Override
  public void registerFlushAllEventHook(final VoidCallable onFlushAllEventHook) {
    this.onFlushAllEventHook = onFlushAllEventHook;
  }

  @Override
  public void addRecord(final AirbyteStreamNameNamespacePair stream, final AirbyteMessage message) throws Exception {

    final SerializableBuffer streamBuffer = allBuffers.computeIfAbsent(stream, k -> {
      LOGGER.info("Starting a new buffer for stream {} (current state: {} in {} buffers)",
          stream.getName(),
          FileUtils.byteCountToDisplaySize(totalBufferSizeInBytes),
          allBuffers.size());
      try {
        return onCreateBuffer.apply(stream, catalog);
      } catch (final Exception e) {
        LOGGER.error("Failed to create a new buffer for stream {}", stream.getName(), e);
        throw new RuntimeException(e);
      }
    });
    if (streamBuffer == null) {
      throw new RuntimeException(String.format("Failed to create/get streamBuffer for stream %s.%s", stream.getNamespace(), stream.getName()));
    }
    final long actualMessageSizeInBytes = streamBuffer.accept(message.getRecord());
    totalBufferSizeInBytes += actualMessageSizeInBytes;
    if (totalBufferSizeInBytes >= streamBuffer.getMaxTotalBufferSizeInBytes()
        || allBuffers.size() >= streamBuffer.getMaxConcurrentStreamsInBuffer()) {
      flushAll();
      totalBufferSizeInBytes = 0;
    } else if (streamBuffer.getByteCount() >= streamBuffer.getMaxPerStreamBufferSizeInBytes()) {
      flushWriter(stream, streamBuffer);
    }
  }

  @Override
  public void flushWriter(final AirbyteStreamNameNamespacePair stream, final SerializableBuffer writer) throws Exception {
    LOGGER.info("Flushing buffer of stream {} ({})", stream.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));
    AirbyteSentry.executeWithTracing("FlushBuffer", () -> {
      onStreamFlush.accept(stream, writer);
    }, Map.of("bufferSizeInBytes", writer.getByteCount()));
    totalBufferSizeInBytes -= writer.getByteCount();
    allBuffers.remove(stream);
  }

  @Override
  public void flushAll() throws Exception {
    LOGGER.info("Flushing all {} current buffers ({} in total)", allBuffers.size(), FileUtils.byteCountToDisplaySize(totalBufferSizeInBytes));
    AirbyteSentry.executeWithTracing("FlushBuffer", () -> {
      for (final Entry<AirbyteStreamNameNamespacePair, SerializableBuffer> entry : allBuffers.entrySet()) {
        LOGGER.info("Flushing buffer of stream {} ({})", entry.getKey().getName(), FileUtils.byteCountToDisplaySize(entry.getValue().getByteCount()));
        onStreamFlush.accept(entry.getKey(), entry.getValue());
      }
      close();
      clear();
    }, Map.of("bufferSizeInBytes", totalBufferSizeInBytes));

    if (onFlushAllEventHook != null) {
      onFlushAllEventHook.call();
    }
    totalBufferSizeInBytes = 0;
  }

  @Override
  public void clear() throws Exception {
    LOGGER.debug("Reset all buffers");
    allBuffers = new HashMap<>();
  }

  @Override
  public void close() throws Exception {
    final List<Exception> exceptionsThrown = new ArrayList<>();
    for (final Entry<AirbyteStreamNameNamespacePair, SerializableBuffer> entry : allBuffers.entrySet()) {
      try {
        LOGGER.info("Closing buffer for stream {}", entry.getKey().getName());
        entry.getValue().close();
      } catch (final Exception e) {
        exceptionsThrown.add(e);
        LOGGER.error("Exception while closing stream buffer", e);
      }
    }
    if (!exceptionsThrown.isEmpty()) {
      throw new RuntimeException(String.format("Exceptions thrown while closing buffers: %s", Strings.join(exceptionsThrown, "\n")));
    }
  }

}
