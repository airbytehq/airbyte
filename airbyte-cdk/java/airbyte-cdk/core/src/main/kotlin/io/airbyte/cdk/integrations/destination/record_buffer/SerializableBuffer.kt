/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.io.*

/**
 * A [SerializableBuffer] is designed to be used as part of a [SerializedBufferingStrategy].
 *
 * It encapsulates the actual implementation of a buffer: both the medium storage (usually defined
 * as part of [BufferStorage]. and the format of the serialized data when it is written to the
 * buffer.
 *
 * A [BaseSerializedBuffer] class is provided, and should be the expected class to derive from when
 * implementing a new format of buffer. The storage aspects are normally provided through
 * composition of [BufferStorage].
 */
interface SerializableBuffer : AutoCloseable {
    /**
     * Adds a [AirbyteRecordMessage] to the buffer and returns the size of the message in bytes
     *
     * @param record [AirbyteRecordMessage] to be added to buffer
     * @return number of bytes written to the buffer
     */
    @Deprecated("")
    @Throws(Exception::class)
    fun accept(record: AirbyteRecordMessage, generationId: Long = 0, syncId: Long = 0): Long

    /**
     * TODO: (ryankfu) Move all destination connectors to pass the serialized record string instead
     * of the entire AirbyteRecordMessage
     *
     * @param recordString serialized record
     * @param airbyteMetaString The serialized airbyte_meta entry
     * @param emittedAt timestamp of the record in milliseconds
     * @return number of bytes written to the buffer
     * @throws Exception
     */
    @Throws(Exception::class)
    fun accept(
        recordString: String,
        airbyteMetaString: String,
        generationId: Long,
        emittedAt: Long
    ): Long

    /** Flush a buffer implementation. */
    @Throws(Exception::class) fun flush()

    /**
     * The buffer implementation should be keeping track of how many bytes it accumulated so far. If
     * any flush events were triggered, the amount of bytes accumulated would also have been
     * decreased accordingly. This method @return such statistics.
     */
    val byteCount: Long

    @get:Throws(IOException::class) val filename: String

    @get:Throws(IOException::class) val file: File?

    @get:Throws(FileNotFoundException::class) val inputStream: InputStream?

    /*
     * Depending on the implementation of the storage, methods below defined reasonable thresholds
     * associated with using this kind of buffer implementation.
     *
     * These could also be dynamically configured/tuned at runtime if needed (from user input for
     * example?)
     */
    /** @return How much storage should be used overall by all buffers */
    val maxTotalBufferSizeInBytes: Long

    /**
     * @return How much storage should be used for a particular stream at a time before flushing it
     */
    val maxPerStreamBufferSizeInBytes: Long

    /** @return How many concurrent buffers can be handled at once in parallel */
    val maxConcurrentStreamsInBuffer: Int
}
