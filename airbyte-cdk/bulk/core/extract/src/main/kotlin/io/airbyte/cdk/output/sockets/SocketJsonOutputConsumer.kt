/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.SequenceWriter
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.output.RecordTemplate
import io.airbyte.cdk.output.StreamToTemplateMap
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.time.Clock
import java.util.concurrent.ConcurrentHashMap

// This class emits Airbyte messages in JSONL format to a socket data channel.
// It accepts a data channel acquired by the caller.
class SocketJsonOutputConsumer(
    private val dataChannel: SocketDataChannel,
    clock: Clock,
    val bufferByteSizeThresholdForFlush: Int,
    private val additionalProperties: Map<String, String>,
) : OutputConsumer(clock) {
    private val log = KotlinLogging.logger {}
    private val buffer = ByteArrayOutputStream()
    private val jsonGenerator: JsonGenerator = Jsons.createGenerator(buffer)
    private val sequenceWriter: SequenceWriter = Jsons.writer().writeValues(buffer)

    override fun accept(airbyteMessage: AirbyteMessage) {
        // This method effectively println's its JSON-serialized argument.
        // Using println is not particularly efficient, however.
        // To improve performance, this method accumulates RECORD messages into a buffer
        // before writing them to standard output in a batch.
        if (airbyteMessage.type == AirbyteMessage.Type.RECORD) {
            // RECORD messages undergo a different serialization scheme.
            accept(airbyteMessage.record)
        } else {
            synchronized(this) {
                // Write a newline character to the buffer if it's not empty.
                withLockMaybeWriteNewline()
                // Non-RECORD AirbyteMessage instances are serialized and written to the buffer
                // using standard jackson object mapping facilities.
                sequenceWriter.write(airbyteMessage)
                sequenceWriter.flush()
                // Such messages don't linger in the buffer, they are flushed to stdout immediately,
                // along with whatever might have already been lingering inside.
                // This prints a newline after the message.
                withLockFlush()
            }
        }
    }

    private fun withLockMaybeWriteNewline() {
        if (buffer.size() > 0) {
            buffer.write('\n'.code)
        }
    }

    override fun close() {
        synchronized(this) {
            // Flush any remaining buffer contents to stdout before closing.
            withLockFlush()
        }
    }

    private fun withLockFlush() {
        if (buffer.size() > 0) {
            buffer.writeTo(dataChannel.outputStream)
            dataChannel.outputStream?.write(System.lineSeparator().toByteArray())
            buffer.reset()
        }
    }

    override fun accept(record: AirbyteRecordMessage) {
        // The serialization of RECORD messages can become a performance bottleneck for source
        // connectors because they can come in much higher volumes than other message types.
        // Specifically, with jackson, the bottleneck is in the object mapping logic.
        // As it turns out, this object mapping logic is not particularly useful for RECORD messages
        // because within a given stream the only variations occur in the "data" and the "meta"
        // fields:
        // - the "data" field is already an ObjectNode and is cheap to serialize,
        // - the "meta" field is often unset.
        // For this reason, this method builds and reuses a JSON template for each stream.
        // Then, for each record, it serializes just "data" and "meta" to populate the template.
        val template: RecordTemplate = getOrCreateRecordTemplate(record.stream, record.namespace)
        synchronized(this) {
            // Write a newline character to the buffer if it's not empty.
            withLockMaybeWriteNewline()
            buffer.write(template.prefix)
            // Serialize the record data ObjectNode to JSON, writing it to the buffer.
            Jsons.writeTree(jsonGenerator, record.data)
            jsonGenerator.flush()
            // If the record has a AirbyteRecordMessageMeta instance set,
            // write ',"meta":' followed by the serialized meta.
            val meta: AirbyteRecordMessageMeta? = record.meta
            if (meta != null) {
                buffer.write(metaPrefixBytes)
                sequenceWriter.write(meta)
                sequenceWriter.flush()
            }
            buffer.write(template.suffix)
            // Flush the buffer to stdout only once it has reached a certain size.
            // Flushing to stdout incurs some overhead (mutex, syscall, etc.)
            // which otherwise becomes very apparent when lots of tiny records are involved.
            if (buffer.size() >= bufferByteSizeThresholdForFlush) {
                withLockFlush()
            }
        }
    }

    private val metaPrefixBytes: ByteArray = META_PREFIX.toByteArray()

    private fun getOrCreateRecordTemplate(stream: String, namespace: String?): RecordTemplate {
        val streamToTemplateMap: StreamToTemplateMap =
            if (namespace == null) {
                unNamespacedTemplates
            } else {
                namespacedTemplates.getOrPut(namespace) { StreamToTemplateMap() }
            }
        return streamToTemplateMap.getOrPut(stream) {
            RecordTemplate.create(
                stream,
                namespace,
                recordEmittedAt,
                additionalProperties,
            )
        }
    }

    private val namespacedTemplates = ConcurrentHashMap<String, StreamToTemplateMap>()
    private val unNamespacedTemplates = StreamToTemplateMap()

    companion object {
        const val META_PREFIX = ""","meta":"""
    }
}
