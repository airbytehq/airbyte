/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.io.*
import java.nio.file.Files
import java.util.*

/**
 * Instead of storing buffered data on disk like the [FileBuffer], this [BufferStorage]
 * accumulates message data in-memory instead. Thus, a bigger heap size would be required.
 */
class InMemoryBuffer(private val fileExtension: String) : BufferStorage {
    private val byteBuffer = ByteArrayOutputStream()
    private var tempFile: File? = null
    override var filename: String? = null

    override val outputStream: OutputStream
        get() = byteBuffer

    override fun getFilename(): String {
        if (filename == null) {
            filename = UUID.randomUUID().toString()
        }
        return filename!!
    }

    @get:Throws(IOException::class)
    override val file: File?
        get() {
            if (tempFile == null) {
                tempFile = Files.createTempFile(getFilename(), fileExtension).toFile()
            }
            return tempFile
        }

    override fun convertToInputStream(): InputStream {
        return ByteArrayInputStream(byteBuffer.toByteArray())
    }

    @Throws(IOException::class)
    override fun close() {
        byteBuffer.close()
    }

    @Throws(IOException::class)
    override fun deleteFile() {
        if (tempFile != null) {
            LOGGER.info("Deleting tempFile data {}", getFilename())
            Files.deleteIfExists(tempFile!!.toPath())
        }
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(InMemoryBuffer::class.java)

        // The per stream size limit is following recommendations from:
        // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
        // "To optimize the number of parallel operations for a load,
        // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size compressed."
        val maxPerStreamBufferSizeInBytes: Long = (200 * 1024 * 1024 // 200 MB
                ).toLong()
            get() = Companion.field

        // Other than the per-file size limit, we also limit the total size (which would limit how many
        // concurrent streams we can buffer simultaneously too)
        // Since this class is storing data in memory, the buffer size limits below are tied to the
        // necessary RAM space.
        val maxTotalBufferSizeInBytes: Long = (1024 * 1024 * 1024 // 1 GB
                ).toLong()
            get() = Companion.field

        // we limit number of stream being buffered simultaneously anyway
        val maxConcurrentStreamsInBuffer: Int = 100
            get() = Companion.field
    }
}
