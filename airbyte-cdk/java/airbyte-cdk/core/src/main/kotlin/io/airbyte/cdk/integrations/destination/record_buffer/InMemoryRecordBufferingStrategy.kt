/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.record_buffer

import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.CheckAndRemoveRecordWriter
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordSizeEstimator
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordWriter
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import java.util.*
import org.apache.commons.io.FileUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * This is the default implementation of a [BufferStorage] to be backward compatible. Data is being
 * buffered in a [<] as they are being consumed.
 *
 * This should be deprecated as we slowly move towards using [SerializedBufferingStrategy] instead.
 */
class InMemoryRecordBufferingStrategy(
    private val recordWriter: RecordWriter<AirbyteRecordMessage>,
    private val checkAndRemoveRecordWriter: CheckAndRemoveRecordWriter?,
    private val maxQueueSizeInBytes: Long
) : BufferingStrategy {
    private var streamBuffer:
        MutableMap<AirbyteStreamNameNamespacePair, MutableList<AirbyteRecordMessage>> =
        HashMap()
    private var fileName: String? = null

    private val recordSizeEstimator = RecordSizeEstimator()
    private var bufferSizeInBytes: Long = 0

    constructor(
        recordWriter: RecordWriter<AirbyteRecordMessage>,
        maxQueueSizeInBytes: Long
    ) : this(recordWriter, null, maxQueueSizeInBytes)

    @Throws(Exception::class)
    override fun addRecord(
        stream: AirbyteStreamNameNamespacePair,
        message: AirbyteMessage
    ): Optional<BufferFlushType> {
        var flushed: Optional<BufferFlushType> = Optional.empty()

        val messageSizeInBytes = recordSizeEstimator.getEstimatedByteSize(message.record)
        if (bufferSizeInBytes + messageSizeInBytes > maxQueueSizeInBytes) {
            flushAllBuffers()
            flushed = Optional.of(BufferFlushType.FLUSH_ALL)
        }

        val bufferedRecords =
            streamBuffer.computeIfAbsent(stream) { _: AirbyteStreamNameNamespacePair ->
                ArrayList()
            }
        bufferedRecords.add(message.record)
        bufferSizeInBytes += messageSizeInBytes

        return flushed
    }

    @Throws(Exception::class)
    override fun flushSingleBuffer(
        stream: AirbyteStreamNameNamespacePair,
        buffer: SerializableBuffer
    ) {
        LOGGER.info(
            "Flushing single stream {}: {} records",
            stream.name,
            streamBuffer[stream]!!.size
        )
        recordWriter.accept(stream, streamBuffer[stream]!!)
        LOGGER.info("Flushing completed for {}", stream.name)
    }

    @Throws(Exception::class)
    override fun flushAllBuffers() {
        for ((key, value) in streamBuffer) {
            LOGGER.info(
                "Flushing {}: {} records ({})",
                key.name,
                value.size,
                FileUtils.byteCountToDisplaySize(bufferSizeInBytes)
            )
            recordWriter.accept(key, value)
            if (checkAndRemoveRecordWriter != null) {
                fileName = checkAndRemoveRecordWriter.apply(key, fileName)
            }
            LOGGER.info("Flushing completed for {}", key.name)
        }
        close()
        clear()
        bufferSizeInBytes = 0
    }

    override fun clear() {
        streamBuffer = HashMap()
    }

    @Throws(Exception::class) override fun close() {}

    companion object {
        private val LOGGER: Logger =
            LoggerFactory.getLogger(InMemoryRecordBufferingStrategy::class.java)
    }
}
