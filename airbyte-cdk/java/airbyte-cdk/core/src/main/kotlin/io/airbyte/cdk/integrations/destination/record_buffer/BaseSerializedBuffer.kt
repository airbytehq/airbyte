/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import com.google.common.io.CountingOutputStream
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.*
import org.apache.commons.compress.compressors.gzip.GzipCompressorOutputStream
import org.apache.commons.io.FileUtils

private val LOGGER = KotlinLogging.logger {}
/**
 * Base implementation of a [SerializableBuffer]. It is composed of a [BufferStorage] where the
 * actual data is being stored in a serialized format.
 *
 * Such data format is defined by concrete implementation inheriting from this base abstract class.
 * To do so, necessary methods on handling "writer" methods should be defined. This writer would
 * take care of converting [AirbyteRecordMessage] into the serialized form of the data such as it
 * can be stored in the outputStream of the [BufferStorage].
 */
abstract class BaseSerializedBuffer
protected constructor(private val bufferStorage: BufferStorage) : SerializableBuffer {
    private val byteCounter = CountingOutputStream(bufferStorage.getOutputStream())

    private var useCompression = true
    private var compressedBuffer: GzipCompressorOutputStream? = null
    override var inputStream: InputStream? = null
    private var isStarted = false
    private var isClosed = false

    /**
     * Initializes the writer objects such that it can now write to the downstream @param
     * outputStream
     */
    @Throws(Exception::class) protected abstract fun initWriter(outputStream: OutputStream)

    /**
     * Transform the @param record into a serialized form of the data and writes it to the
     * registered OutputStream provided when [BaseSerializedBuffer.initWriter] was called.
     */
    @Deprecated("")
    @Throws(IOException::class)
    protected abstract fun writeRecord(record: AirbyteRecordMessage)

    /**
     * TODO: (ryankfu) move destination to use serialized record string instead of passing entire
     * AirbyteRecord
     *
     * @param recordString serialized record
     * @param airbyteMetaString
     * @param emittedAt timestamp of the record in milliseconds
     * @throws IOException
     */
    @Throws(IOException::class)
    protected abstract fun writeRecord(
        recordString: String,
        airbyteMetaString: String,
        emittedAt: Long
    )

    /**
     * Stops the writer from receiving new data and prepares it for being finalized and converted
     * into an InputStream to read from instead. This is used when flushing the buffer into some
     * other destination.
     */
    @Throws(IOException::class) protected abstract fun flushWriter()

    @Throws(IOException::class) protected abstract fun closeWriter()

    fun withCompression(useCompression: Boolean): SerializableBuffer {
        if (!isStarted) {
            this.useCompression = useCompression
            return this
        }
        throw RuntimeException("Options should be configured before starting to write")
    }

    @Deprecated("")
    @Throws(Exception::class)
    override fun accept(record: AirbyteRecordMessage): Long {
        if (!isStarted) {
            if (useCompression) {
                compressedBuffer = GzipCompressorOutputStream(byteCounter)
                initWriter(compressedBuffer!!)
            } else {
                initWriter(byteCounter)
            }
            isStarted = true
        }
        if (inputStream == null && !isClosed) {
            val startCount = byteCounter.count
            @Suppress("deprecation") writeRecord(record)
            return byteCounter.count - startCount
        } else {
            throw IllegalCallerException("Buffer is already closed, it cannot accept more messages")
        }
    }

    @Throws(Exception::class)
    override fun accept(recordString: String, airbyteMetaString: String, emittedAt: Long): Long {
        if (!isStarted) {
            if (useCompression) {
                compressedBuffer = GzipCompressorOutputStream(byteCounter)
                initWriter(compressedBuffer!!)
            } else {
                initWriter(byteCounter)
            }
            isStarted = true
        }
        if (inputStream == null && !isClosed) {
            val startCount = byteCounter.count
            writeRecord(recordString, airbyteMetaString, emittedAt)
            return byteCounter.count - startCount
        } else {
            throw IllegalCallerException("Buffer is already closed, it cannot accept more messages")
        }
    }

    override val filename: String
        @Throws(IOException::class)
        get() {
            if (useCompression && !bufferStorage.filename.endsWith(GZ_SUFFIX)) {
                return bufferStorage.filename + GZ_SUFFIX
            }
            return bufferStorage.filename
        }

    override val file: File?
        @Throws(IOException::class)
        get() {
            if (useCompression && !bufferStorage.filename.endsWith(GZ_SUFFIX)) {
                if (bufferStorage.file.renameTo(File(bufferStorage.filename + GZ_SUFFIX))) {
                    LOGGER.info { "Renaming compressed file to include .gz file extension" }
                }
            }
            return bufferStorage.file
        }

    @Throws(IOException::class)
    protected fun convertToInputStream(): InputStream {
        return bufferStorage.convertToInputStream()
    }

    @Throws(IOException::class)
    override fun flush() {
        if (inputStream == null && !isClosed) {
            flushWriter()
            LOGGER.debug { "Wrapping up compression and write GZIP trailer data." }
            compressedBuffer?.flush()
            compressedBuffer?.close()
            closeWriter()
            bufferStorage.close()
            inputStream = convertToInputStream()
            LOGGER.info {
                "Finished writing data to $filename (${FileUtils.byteCountToDisplaySize(byteCounter.count)})"
            }
        }
    }

    override val byteCount: Long
        get() = byteCounter.count

    @Throws(Exception::class)
    override fun close() {
        if (!isClosed) {
            // inputStream can be null if the accept method encounters
            // an error before inputStream is initialized
            inputStream?.close()
            bufferStorage.deleteFile()
            isClosed = true
        }
    }

    override val maxTotalBufferSizeInBytes: Long = bufferStorage.maxTotalBufferSizeInBytes

    override val maxPerStreamBufferSizeInBytes: Long = bufferStorage.maxPerStreamBufferSizeInBytes

    override val maxConcurrentStreamsInBuffer: Int = bufferStorage.maxConcurrentStreamsInBuffer

    companion object {

        private const val GZ_SUFFIX = ".gz"
    }
}
