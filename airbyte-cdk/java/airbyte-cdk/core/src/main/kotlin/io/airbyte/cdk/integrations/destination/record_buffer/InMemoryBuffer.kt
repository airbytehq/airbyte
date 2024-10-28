/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.*
import java.nio.file.Files
import java.util.*

private val LOGGER = KotlinLogging.logger {}
/**
 * Instead of storing buffered data on disk like the [FileBuffer], this [BufferStorage] accumulates
 * message data in-memory instead. Thus, a bigger heap size would be required.
 */
class InMemoryBuffer(private val fileExtension: String) : BufferStorage {
    private val byteBuffer = ByteArrayOutputStream()
    private var tempFile: File? = null
    override var filename: String = UUID.randomUUID().toString()

    // The per stream size limit is following recommendations from:
    // https://docs.snowflake.com/en/user-guide/data-load-considerations-prepare.html#general-file-sizing-recommendations
    // "To optimize the number of parallel operations for a load,
    // we recommend aiming to produce data files roughly 100-250 MB (or larger) in size compressed."
    override val maxPerStreamBufferSizeInBytes: Long =
        (200 * 1024 * 1024 // 200 MB
            )
            .toLong()

    // Other than the per-file size limit, we also limit the total size (which would limit how many
    // concurrent streams we can buffer simultaneously too)
    // Since this class is storing data in memory, the buffer size limits below are tied to the
    // necessary RAM space.
    override val maxTotalBufferSizeInBytes: Long =
        (1024 * 1024 * 1024 // 1 GB
            )
            .toLong()

    // we limit number of stream being buffered simultaneously anyway
    override val maxConcurrentStreamsInBuffer: Int = 100

    override fun getOutputStream(): OutputStream {
        return byteBuffer
    }

    @get:Throws(IOException::class)
    override val file: File
        get() {
            val tempFile = this.tempFile ?: Files.createTempFile(filename, fileExtension).toFile()
            this.tempFile = tempFile
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
        var pathToDelete = tempFile?.toPath()
        if (pathToDelete != null) {
            LOGGER.info { "Deleting tempFile data $filename" }
            Files.deleteIfExists(pathToDelete)
        }
    }
}
