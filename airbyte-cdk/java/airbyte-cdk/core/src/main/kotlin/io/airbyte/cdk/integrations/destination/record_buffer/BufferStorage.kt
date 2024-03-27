/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import java.io.*

/**
 * This interface abstract the actual object that is used to store incoming data being buffered. It
 * could be a file, in-memory or some other objects.
 *
 * However, in order to be used as part of the [SerializableBuffer], this [BufferStorage] should
 * implement some methods used to determine how to write into and read from the storage once we are
 * done buffering
 *
 * Some easy methods for manipulating the storage viewed as a file or InputStream are therefore
 * required.
 *
 * Depending on the implementation of the storage medium, it would also determine what storage
 * limits are possible.
 */
interface BufferStorage {
    @get:Throws(IOException::class) val filename: String

    @get:Throws(IOException::class) val file: File

    /**
     * Once buffering has reached some limits, the storage stream should be turned into an
     * InputStream. This method should assume we are not going to write to buffer anymore, and it is
     * safe to convert to some other format to be read from now.
     */
    @Throws(IOException::class) fun convertToInputStream(): InputStream

    @Throws(IOException::class) fun close()

    /** Cleans-up any file that was produced in the process of buffering (if any were produced) */
    @Throws(IOException::class) fun deleteFile()

    @Throws(IOException::class) fun getOutputStream(): OutputStream

    /*
     * Depending on the implementation of the storage, methods below defined reasonable thresholds
     * associated with using this kind of buffer storage.
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
