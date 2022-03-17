/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.record_buffer;

import io.airbyte.commons.concurrency.VoidCallable;
import io.airbyte.integrations.base.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.AirbyteMessage;

/**
 * High-level interface used by
 * {@link io.airbyte.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer}
 *
 * A Record buffer strategy relies on the capacity available of underlying
 * {@link RecordBufferImplementation} to determine what to do when consuming a new
 * {@link AirbyteMessage} into the buffer. And when to
 *
 */
public interface RecordBufferingStrategy extends AutoCloseable {

  /**
   * Add a new message to the buffer while consuming streams
   */
  void addRecord(AirbyteStreamNameNamespacePair stream, AirbyteMessage message) throws Exception;

  /**
   * Flush buffered messages in a writer from a particular stream
   */
  void flushWriter(AirbyteStreamNameNamespacePair stream, RecordBufferImplementation writer) throws Exception;

  /**
   * Flush all writers that were buffering message data so far.
   */
  void flushAll() throws Exception;

  /**
   * Removes all stream buffers.
   */
  void clear() throws Exception;

  /**
   * When all buffers are being flushed, we can signal some parent function of this event for further
   * processing.
   *
   * THis install such a hook to be triggered when that happens.
   */
  void registerFlushAllEventHook(VoidCallable onFlushAllEventHook);

}
