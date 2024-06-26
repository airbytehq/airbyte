/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.*
import org.apache.commons.io.FileUtils

private val LOGGER = KotlinLogging.logger {}
/**
 * Buffering Strategy used to convert [io.airbyte.protocol.models.AirbyteRecordMessage] into a
 * stream of bytes to more readily save and transmit information
 *
 * This class is meant to be used in conjunction with [SerializableBuffer]
 */
class SerializedBufferingStrategy
/**
 * Creates instance of Serialized Buffering Strategy used to handle the logic of flushing buffer
 * with an associated buffer type
 *
 * @param onCreateBuffer type of buffer used upon creation
 * @param catalog collection of [io.airbyte.protocol.models.ConfiguredAirbyteStream]
 * @param onStreamFlush buffer flush logic used throughout the streaming of messages
 */
(
    private val onCreateBuffer: BufferCreateFunction,
    private val catalog: ConfiguredAirbyteCatalog,
    private val onStreamFlush: FlushBufferFunction
) : BufferingStrategy {
    private var allBuffers: MutableMap<AirbyteStreamNameNamespacePair, SerializableBuffer> =
        HashMap()
    private var totalBufferSizeInBytes: Long = 0

    /**
     * Handles both adding records and when buffer is full to also flush
     *
     * @param stream stream associated with record
     * @param message [AirbyteMessage] to buffer
     * @return Optional which contains a [BufferFlushType] if a flush occurred, otherwise empty)
     */
    @Throws(Exception::class)
    override fun addRecord(
        stream: AirbyteStreamNameNamespacePair,
        message: AirbyteMessage
    ): Optional<BufferFlushType> {
        var flushed: Optional<BufferFlushType> = Optional.empty()

        val buffer = getOrCreateBuffer(stream)

        @Suppress("DEPRECATION") val actualMessageSizeInBytes = buffer.accept(message.record)
        totalBufferSizeInBytes += actualMessageSizeInBytes
        // Flushes buffer when either the buffer was completely filled or only a single stream was
        // filled
        if (
            totalBufferSizeInBytes >= buffer.maxTotalBufferSizeInBytes ||
                allBuffers.size >= buffer.maxConcurrentStreamsInBuffer
        ) {
            flushAllBuffers()
            flushed = Optional.of(BufferFlushType.FLUSH_ALL)
        } else if (buffer.byteCount >= buffer.maxPerStreamBufferSizeInBytes) {
            flushSingleBuffer(stream, buffer)
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
            flushed = Optional.of(BufferFlushType.FLUSH_SINGLE_STREAM)
        }
        return flushed
    }

    /**
     * Creates a new buffer for each stream if buffers do not already exist, else return already
     * computed buffer
     */
    private fun getOrCreateBuffer(stream: AirbyteStreamNameNamespacePair): SerializableBuffer {
        return allBuffers.computeIfAbsent(stream) { _: AirbyteStreamNameNamespacePair ->
            LOGGER.info {
                "Starting a new buffer for stream ${stream.name} (current state: ${FileUtils.byteCountToDisplaySize(totalBufferSizeInBytes)} in ${allBuffers.size} buffers)"
            }
            try {
                return@computeIfAbsent onCreateBuffer.apply(stream, catalog)!!
            } catch (e: Exception) {
                LOGGER.error(e) { "Failed to create a new buffer for stream ${stream.name}" }
                throw RuntimeException(e)
            }
        }
    }

    @Throws(Exception::class)
    override fun flushSingleBuffer(
        stream: AirbyteStreamNameNamespacePair,
        buffer: SerializableBuffer
    ) {
        LOGGER.info {
            "Flushing buffer of stream ${stream.name} (${FileUtils.byteCountToDisplaySize(buffer.byteCount)})"
        }
        onStreamFlush.accept(stream, buffer)
        totalBufferSizeInBytes -= buffer.byteCount
        allBuffers.remove(stream)
        LOGGER.info { "Flushing completed for ${stream.name}" }
    }

    @Throws(Exception::class)
    override fun flushAllBuffers() {
        LOGGER.info {
            "Flushing all ${allBuffers.size} current buffers (${FileUtils.byteCountToDisplaySize(totalBufferSizeInBytes)} in total)"
        }
        for ((stream, buffer) in allBuffers) {
            LOGGER.info {
                "Flushing buffer of stream ${stream.name} (${FileUtils.byteCountToDisplaySize(buffer.byteCount)})"
            }
            onStreamFlush.accept(stream, buffer)
            LOGGER.info { "Flushing completed for ${stream.name}" }
        }
        close()
        clear()
        totalBufferSizeInBytes = 0
    }

    @Throws(Exception::class)
    override fun clear() {
        LOGGER.debug { "Reset all buffers" }
        allBuffers = HashMap()
    }

    @Throws(Exception::class)
    override fun close() {
        val exceptionsThrown: MutableList<Exception> = ArrayList()
        for ((stream, buffer) in allBuffers) {
            try {
                LOGGER.info { "Closing buffer for stream ${stream.name}" }
                buffer.close()
            } catch (e: Exception) {
                exceptionsThrown.add(e)
                LOGGER.error(e) { "Exception while closing stream buffer" }
            }
        }

        ConnectorExceptionUtil.logAllAndThrowFirst(
            "Exceptions thrown while closing buffers: ",
            exceptionsThrown
        )
    }
}
