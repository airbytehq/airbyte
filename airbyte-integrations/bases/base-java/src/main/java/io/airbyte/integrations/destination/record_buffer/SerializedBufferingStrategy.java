/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.commons.string.Strings;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Buffering Strategy used to convert {@link io.airbyte.protocol.models.AirbyteRecordMessage} into a
 * stream of bytes to more readily save and transmit information
 *
 * <p>
 * This class is meant to be used in conjunction with {@link SerializableBuffer}
 * </p>
 */
public class SerializedBufferingStrategy implements BufferingStrategy {

  private static final Logger LOGGER = LoggerFactory.getLogger(SerializedBufferingStrategy.class);

  private final BufferCreateFunction onCreateBuffer;
  private final FlushBufferFunction onStreamFlush;

  private Map<AirbyteStreamNameNamespacePair, SerializableBuffer> allBuffers = new HashMap<>();
  private long totalBufferSizeInBytes;
  private final ConfiguredAirbyteCatalog catalog;

  /**
   * Creates instance of Serialized Buffering Strategy used to handle the logic of flushing buffer
   * with an associated buffer type
   *
   * @param onCreateBuffer type of buffer used upon creation
   * @param catalog collection of {@link io.airbyte.protocol.models.ConfiguredAirbyteStream}
   * @param onStreamFlush buffer flush logic used throughout the streaming of messages
   */
  public SerializedBufferingStrategy(final BufferCreateFunction onCreateBuffer,
                                     final ConfiguredAirbyteCatalog catalog,
                                     final FlushBufferFunction onStreamFlush) {
    this.onCreateBuffer = onCreateBuffer;
    this.catalog = catalog;
    this.onStreamFlush = onStreamFlush;
    this.totalBufferSizeInBytes = 0;
  }

  /**
   * Handles both adding records and when buffer is full to also flush
   *
   * @param stream stream associated with record
   * @param message {@link AirbyteMessage} to buffer
   * @return Optional which contains a {@link BufferFlushType} if a flush occurred, otherwise empty)
   * @throws Exception
   */
  @Override
  public Optional<BufferFlushType> addRecord(final AirbyteStreamNameNamespacePair stream, final AirbyteMessage message) throws Exception {
    Optional<BufferFlushType> flushed = Optional.empty();

    final SerializableBuffer buffer = getOrCreateBuffer(stream);
    if (buffer == null) {
      throw new RuntimeException(String.format("Failed to create/get buffer for stream %s.%s", stream.getNamespace(), stream.getName()));
    }

    final long actualMessageSizeInBytes = buffer.accept(message.getRecord());
    totalBufferSizeInBytes += actualMessageSizeInBytes;
    // Flushes buffer when either the buffer was completely filled or only a single stream was filled
    if (totalBufferSizeInBytes >= buffer.getMaxTotalBufferSizeInBytes()
        || allBuffers.size() >= buffer.getMaxConcurrentStreamsInBuffer()) {
      flushAllBuffers();
      flushed = Optional.of(BufferFlushType.FLUSH_ALL);
    } else if (buffer.getByteCount() >= buffer.getMaxPerStreamBufferSizeInBytes()) {
      flushSingleBuffer(stream, buffer);
      /*
       * Note: This branch is needed to indicate to the {@link DefaultDestStateLifeCycleManager} that an
       * individual stream was flushed, there is no guarantee that it will flush records in the same order
       * that state messages were received. The outcome here is that records get flushed but our updating
       * of which state messages have been flushed falls behind.
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
      flushed = Optional.of(BufferFlushType.FLUSH_SINGLE_STREAM);
    }
    return flushed;
  }

  /**
   * Creates a new buffer for each stream if buffers do not already exist, else return already
   * computed buffer
   */
  private SerializableBuffer getOrCreateBuffer(final AirbyteStreamNameNamespacePair stream) {
    return allBuffers.computeIfAbsent(stream, k -> {
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
  }

  @Override
  public void flushSingleBuffer(final AirbyteStreamNameNamespacePair stream, final SerializableBuffer buffer) throws Exception {
    LOGGER.info("Flushing buffer of stream {} ({})", stream.getName(), FileUtils.byteCountToDisplaySize(buffer.getByteCount()));
    onStreamFlush.accept(stream, buffer);
    totalBufferSizeInBytes -= buffer.getByteCount();
    allBuffers.remove(stream);
    LOGGER.info("Flushing completed for {}", stream.getName());
  }

  @Override
  public void flushAllBuffers() throws Exception {
    LOGGER.info("Flushing all {} current buffers ({} in total)", allBuffers.size(), FileUtils.byteCountToDisplaySize(totalBufferSizeInBytes));
    for (final Entry<AirbyteStreamNameNamespacePair, SerializableBuffer> entry : allBuffers.entrySet()) {
      final AirbyteStreamNameNamespacePair stream = entry.getKey();
      final SerializableBuffer buffer = entry.getValue();
      LOGGER.info("Flushing buffer of stream {} ({})", stream.getName(), FileUtils.byteCountToDisplaySize(buffer.getByteCount()));
      onStreamFlush.accept(stream, buffer);
      LOGGER.info("Flushing completed for {}", stream.getName());
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
        final AirbyteStreamNameNamespacePair stream = entry.getKey();
        LOGGER.info("Closing buffer for stream {}", stream.getName());
        final SerializableBuffer buffer = entry.getValue();
        buffer.close();
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
