/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.commons.functional.CheckedBiConsumer;
import io.airbyte.commons.functional.CheckedBiFunction;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
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
  }

  @Override
  public boolean addRecord(final AirbyteStreamNameNamespacePair stream, final AirbyteMessage message) throws Exception {
    boolean didFlush = false;

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
      didFlush = true;
      totalBufferSizeInBytes = 0;
    } else if (streamBuffer.getByteCount() >= streamBuffer.getMaxPerStreamBufferSizeInBytes()) {
      flushWriter(stream, streamBuffer);
      /*
       * Note: We intentionally do not mark didFlush as true in the branch of this conditional. Because
       * this branch flushes individual streams, there is no guaranteee that it will flush records in the
       * same order that state messages were received. The outcome here is that records get flushed but
       * our updating of which state messages have been flushed falls behind.
       *
       * This is not ideal from a checkpoint point of view, because it means in the case where there is a
       * failure, we will not be able to report that those records that were flushed and committed were
       * committed because there corresponding state messages weren't marked as flushed. Thus, it weakens
       * checkpointing, but it does not cause a correctness issue.
       *
       * In non-failure cases, using this conditional branch relies on the state messages getting flushed
       * by some other means. That can be caused by the previous branch in this conditional. It is
       * guaranteed by the fact that we always flush all state messages at the end of a sync.
       */
    }

    return didFlush;
  }

  @Override
  public void flushWriter(final AirbyteStreamNameNamespacePair stream, final SerializableBuffer writer) throws Exception {
    LOGGER.info("Flushing buffer of stream {} ({})", stream.getName(), FileUtils.byteCountToDisplaySize(writer.getByteCount()));
    onStreamFlush.accept(stream, writer);
    totalBufferSizeInBytes -= writer.getByteCount();
    allBuffers.remove(stream);
  }

  @Override
  public void flushAll() throws Exception {
    LOGGER.info("Flushing all {} current buffers ({} in total)", allBuffers.size(), FileUtils.byteCountToDisplaySize(totalBufferSizeInBytes));
    for (final Entry<AirbyteStreamNameNamespacePair, SerializableBuffer> entry : allBuffers.entrySet()) {
      LOGGER.info("Flushing buffer of stream {} ({})", entry.getKey().getName(), FileUtils.byteCountToDisplaySize(entry.getValue().getByteCount()));
      onStreamFlush.accept(entry.getKey(), entry.getValue());
    }
    close();
    clear();

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
