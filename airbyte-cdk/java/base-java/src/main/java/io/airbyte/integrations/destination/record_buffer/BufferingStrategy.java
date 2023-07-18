/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.Optional;

/**
 * High-level interface used by
 * {@link io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer}
 *
 * A Record buffering strategy relies on the capacity available of underlying
 * {@link SerializableBuffer} to determine what to do when consuming a new {@link AirbyteMessage}
 * into the buffer. It also defines when to flush such buffers and how to empty them once they fill
 * up.
 *
 */
public interface BufferingStrategy extends AutoCloseable {

  /**
   * Add a new message to the buffer while consuming streams, also handles when a buffer flush when
   * buffer has been filled
   *
   * @param stream stream associated with record
   * @param message {@link AirbyteMessage} to be added to the buffer
   * @return an optional value if a flushed occur with the respective flush type, otherwise an empty
   *         value means only a record was added
   * @throws Exception throw on failure
   */
  Optional<BufferFlushType> addRecord(AirbyteStreamNameNamespacePair stream, AirbyteMessage message) throws Exception;

  /**
   * Flush buffered messages in a buffer from a particular stream
   */
  void flushSingleBuffer(AirbyteStreamNameNamespacePair stream, SerializableBuffer buffer) throws Exception;

  /**
   * Flush all buffers that were buffering message data so far.
   */
  void flushAllBuffers() throws Exception;

  /**
   * Removes all stream buffers.
   */
  void clear() throws Exception;

}
