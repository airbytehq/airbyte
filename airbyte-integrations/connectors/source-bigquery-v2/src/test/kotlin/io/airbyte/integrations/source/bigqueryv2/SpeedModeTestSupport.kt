/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.bigqueryv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.protocol.AirbyteValueProtobufDecoder
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteMessage.AirbyteMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.io.ByteArrayInputStream
import java.io.ByteArrayOutputStream
import java.io.IOException
import java.math.BigDecimal
import java.math.BigInteger
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.ByteBuffer
import java.nio.channels.SocketChannel
import java.nio.file.Files
import java.nio.file.Path
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime

/**
 * Test-side view of the speed data channel: decodes what the connector writes to its Unix domain
 * sockets (`DATA_CHANNEL_MEDIUM=SOCKET`) in either `DATA_CHANNEL_FORMAT`, and renders protobuf
 * values as the JSON the STDIO channel would have emitted for the same column, so that both
 * channels can be compared record by record.
 */
object SpeedModeTestSupport {

    private val decoder = AirbyteValueProtobufDecoder()

    /**
     * The JSON rendering of a decoded protobuf value ([AirbyteValueProtobufDecoder.decode]) for a
     * column whose catalog JSON schema is [jsonSchema]. Objects, arrays and `airbyte_type: json`
     * columns travel as serialized JSON text; temporals are rendered with the CDK codecs, which is
     * what the connector's field types use on the STDIO channel too.
     */
    fun protobufValueToJson(decoded: Any?, jsonSchema: JsonNode): JsonNode =
        when (decoded) {
            null -> Jsons.nullNode()
            is Boolean -> Jsons.booleanNode(decoded)
            is String ->
                if (isJsonColumn(jsonSchema)) Jsons.readTree(decoded) else Jsons.textNode(decoded)
            is BigInteger -> Jsons.numberNode(BigDecimal(decoded))
            is BigDecimal -> Jsons.numberNode(decoded)
            is LocalDate -> LocalDateCodec.encode(decoded)
            is LocalTime -> LocalTimeCodec.encode(decoded)
            is LocalDateTime -> LocalDateTimeCodec.encode(decoded)
            is OffsetDateTime -> OffsetDateTimeCodec.encode(decoded)
            is OffsetTime -> OffsetTimeCodec.encode(decoded)
            else -> throw IllegalArgumentException("unexpected decoded value $decoded")
        }

    fun decode(value: AirbyteValueProtobuf): Any? = decoder.decode(value)

    private fun isJsonColumn(jsonSchema: JsonNode): Boolean {
        val types: Set<String> =
            when (val type = jsonSchema["type"]) {
                null -> emptySet()
                is ArrayNode -> type.map { it.asText() }.toSet()
                else -> setOf(type.asText())
            }
        return "object" in types ||
            "array" in types ||
            jsonSchema["airbyte_type"]?.asText() == "json"
    }

    /**
     * Makes JSON values comparable across channels: every number becomes its plain decimal text
     * (the protobuf channel carries `INT64` as an integer and `FLOAT64` as a double, the STDIO
     * channel emits Jackson number nodes of various classes), and binary nodes become their base64
     * text (the STDIO channel emits `BYTES` as a binary node, the protobuf channel as base64), and
     * object keys are sorted (the protobuf channel orders fields alphabetically).
     */
    fun normalize(node: JsonNode): JsonNode =
        when {
            node.isNumber ->
                Jsons.textNode(node.decimalValue().stripTrailingZeros().toPlainString())
            node.isBinary -> Jsons.textNode(node.asText())
            node.isObject -> {
                // Sorted keys, so that the serialized form is canonical too.
                val result: ObjectNode = Jsons.objectNode()
                node
                    .fields()
                    .asSequence()
                    .sortedBy { it.key }
                    .forEach { (k, v) -> result.set<JsonNode>(k, normalize(v)) }
                result
            }
            node.isArray -> {
                val result: ArrayNode = Jsons.arrayNode()
                node.forEach { result.add(normalize(it)) }
                result
            }
            else -> node
        }

    /** Every length-delimited [AirbyteMessageProtobuf] in [bytes], probe packets included. */
    fun parseProtobufMessages(bytes: ByteArray): List<AirbyteMessageProtobuf> {
        val input = ByteArrayInputStream(bytes)
        val messages = mutableListOf<AirbyteMessageProtobuf>()
        while (true) {
            val message: AirbyteMessageProtobuf =
                AirbyteMessageProtobuf.parseDelimitedFrom(input) ?: break
            messages.add(message)
        }
        return messages
    }

    /** Every non-blank line of [bytes] parsed as JSON (blank lines are the JSONL probe packets). */
    fun parseJsonlMessages(bytes: ByteArray): List<JsonNode> =
        bytes
            .toString(Charsets.UTF_8)
            .lineSequence()
            .filter { it.isNotBlank() }
            .map { Jsons.readTree(it) }
            .toList()

    /**
     * Client side of one of the connector's Unix domain sockets. The connector binds the socket
     * file and waits for a connection before it assigns the socket to a partition reader, so [poll]
     * connects as soon as the file exists and then drains whatever has been written.
     */
    class UnixSocketReader(val path: Path) : AutoCloseable {
        private var channel: SocketChannel? = null
        private val buffer: ByteBuffer = ByteBuffer.allocate(1 shl 16)
        private val received = ByteArrayOutputStream()
        var closedByPeer: Boolean = false
            private set

        /** Connection attempts refused because the connector was not listening yet. */
        var refusedConnections: Int = 0
            private set

        val isConnected: Boolean
            get() = channel != null

        fun bytes(): ByteArray = received.toByteArray()

        fun poll() {
            if (channel == null) {
                if (!Files.exists(path)) return
                val candidate: SocketChannel = SocketChannel.open(StandardProtocolFamily.UNIX)
                try {
                    candidate.connect(UnixDomainSocketAddress.of(path))
                } catch (e: IOException) {
                    // The connector creates the socket file when it binds and starts listening
                    // right after; a connection attempt in between is refused. Try again later.
                    candidate.close()
                    refusedConnections++
                    return
                }
                candidate.configureBlocking(false)
                channel = candidate
            }
            val open: SocketChannel = channel ?: return
            if (closedByPeer) return
            while (true) {
                buffer.clear()
                val n: Int = open.read(buffer)
                if (n < 0) {
                    closedByPeer = true
                    return
                }
                if (n == 0) return
                received.write(buffer.array(), 0, n)
            }
        }

        override fun close() {
            channel?.close()
        }
    }

    /** Sets JVM system properties for the duration of [block], restoring the previous values. */
    fun <T> withSystemProperties(properties: Map<String, String>, block: () -> T): T {
        val previous: Map<String, String?> =
            properties.keys.associateWith { System.getProperty(it) }
        properties.forEach { (k, v) -> System.setProperty(k, v) }
        try {
            return block()
        } finally {
            previous.forEach { (k, v) ->
                if (v == null) System.clearProperty(k) else System.setProperty(k, v)
            }
        }
    }
}
