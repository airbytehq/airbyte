/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.*

/**
 * High-level interface used by
 * [io.airbyte.cdk.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer]
 *
 * A Record buffering strategy relies on the capacity available of underlying [SerializableBuffer]
 * to determine what to do when consuming a new [AirbyteMessage] into the buffer. It also defines
 * when to flush such buffers and how to empty them once they fill up.
 */
interface BufferingStrategy : AutoCloseable {
    /**
     * Add a new message to the buffer while consuming streams, also handles when a buffer flush
     * when buffer has been filled
     *
     * @param stream stream associated with record
     * @param message [AirbyteMessage] to be added to the buffer
     * @return an optional value if a flushed occur with the respective flush type, otherwise an
     * empty value means only a record was added
     * @throws Exception throw on failure
     */
    @Throws(Exception::class)
    fun addRecord(
        stream: AirbyteStreamNameNamespacePair,
        message: AirbyteMessage
    ): Optional<BufferFlushType>

    /** Flush buffered messages in a buffer from a particular stream */
    @Throws(Exception::class)
    fun flushSingleBuffer(stream: AirbyteStreamNameNamespacePair, buffer: SerializableBuffer)

    /** Flush all buffers that were buffering message data so far. */
    @Throws(Exception::class) fun flushAllBuffers()

    /** Removes all stream buffers. */
    @Throws(Exception::class) fun clear()
}
