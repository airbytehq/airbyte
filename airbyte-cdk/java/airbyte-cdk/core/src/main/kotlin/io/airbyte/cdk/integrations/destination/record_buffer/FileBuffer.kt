/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.*
import java.nio.file.Files
import java.util.*

private val LOGGER = KotlinLogging.logger {}

class FileBuffer : BufferStorage {
    private val fileExtension: String
    private lateinit var tempFile: File
    private var outputStream: OutputStream? = null
    override val maxConcurrentStreamsInBuffer: Int

    // The per stream size limit is following recommendations from:
    // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
    // "To optimize the number of parallel operations for a load,
    // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size compressed."
    override val maxPerStreamBufferSizeInBytes: Long = MAX_PER_STREAM_BUFFER_SIZE_BYTES
    /*
     * Other than the per-file size limit, we also limit the total size (which would limit how many
     * concurrent streams we can buffer simultaneously too) Since this class is storing data on disk,
     * the buffer size limits below are tied to the necessary disk storage space.
     */
    override val maxTotalBufferSizeInBytes: Long = MAX_TOTAL_BUFFER_SIZE_BYTES

    constructor(fileExtension: String) {
        this.fileExtension = fileExtension
        this.maxConcurrentStreamsInBuffer = DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER
    }

    constructor(fileExtension: String, maxConcurrentStreams: Int) {
        this.fileExtension = fileExtension
        this.maxConcurrentStreamsInBuffer = maxConcurrentStreams
    }

    @Throws(IOException::class)
    override fun getOutputStream(): OutputStream {
        if (outputStream == null || !::tempFile.isInitialized) {
            tempFile = Files.createTempFile(UUID.randomUUID().toString(), fileExtension).toFile()
            outputStream = BufferedOutputStream(FileOutputStream(tempFile))
        }
        return outputStream!!
    }

    @get:Throws(IOException::class)
    override val filename: String
        get() = file.name

    @get:Throws(IOException::class)
    override val file: File
        get() {
            if (!::tempFile.isInitialized) {
                getOutputStream()
            }
            return tempFile
        }

    @Throws(IOException::class)
    override fun convertToInputStream(): InputStream {
        return FileInputStream(file)
    }

    @Throws(IOException::class)
    override fun close() {
        outputStream?.close()
    }

    @Throws(IOException::class)
    override fun deleteFile() {
        LOGGER.info { "Deleting tempFile data $filename" }
        Files.deleteIfExists(file.toPath())
    }

    companion object {

        /*
         * We limit number of stream being buffered simultaneously anyway (limit how many files are
         * stored/open for writing)
         *
         * Note: This value can be tuned to increase performance with the tradeoff of increased memory usage
         * (~31 MB per buffer). See {@link StreamTransferManager}
         *
         * For connections with interleaved data (e.g. Change Data Capture), having less buffers than the
         * number of streams being synced will cause buffer thrashing where buffers will need to be flushed
         * before another stream's buffer can be created. Increasing the default max will reduce likelihood
         * of thrashing but not entirely eliminate unless number of buffers equals streams to be synced
         */
        const val DEFAULT_MAX_CONCURRENT_STREAM_IN_BUFFER: Int = 10
        const val FILE_BUFFER_COUNT_KEY: String = "file_buffer_count"

        // This max is subject to change as no proper load testing has been done to verify the side
        // effects
        const val MAX_CONCURRENT_STREAM_IN_BUFFER: Int = 50

        /*
         * Use this soft cap as a guidance for customers to not exceed the recommended number of buffers
         * which is 1 GB (total buffer size) / 31 MB (rough size of each buffer) ~= 32 buffers
         */
        const val SOFT_CAP_CONCURRENT_STREAM_IN_BUFFER: Int = 20

        // The per stream size limit is following recommendations from:
        // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
        // "To optimize the number of parallel operations for a load,
        // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size
        // compressed."
        @JvmStatic
        val MAX_PER_STREAM_BUFFER_SIZE_BYTES: Long =
            (200 * 1024 * 1024 // 200 MB
                )
                .toLong()
        /*
         * Other than the per-file size limit, we also limit the total size (which would limit how many
         * concurrent streams we can buffer simultaneously too) Since this class is storing data on disk,
         * the buffer size limits below are tied to the necessary disk storage space.
         */
        @JvmStatic
        val MAX_TOTAL_BUFFER_SIZE_BYTES: Long =
            (1024 * 1024 * 1024 // 1 GB
                )
                .toLong()
    }
}
