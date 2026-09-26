/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
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

/**
 * Test-side view of the speed data channel: decodes what the connector writes to its Unix domain
 * sockets (`DATA_CHANNEL_MEDIUM=SOCKET`) in either `DATA_CHANNEL_FORMAT`, and renders protobuf
 * values as the JSON the STDIO channel emits for the same attribute, so that the channels can be
 * compared record by record.
 */
object SpeedModeTestSupport {

    private val decoder = AirbyteValueProtobufDecoder()

    /**
     * The JSON the STDIO channel emits for the attribute a protobuf value carries. Values travel
     * typed since the schemas are canonical ([DynamoDbFieldType.airbyteSchemaTypeOf]): a STRING
     * (also a BINARY, which the CDK encodes as its base64 string), an INTEGER, a NUMBER, a BOOLEAN,
     * the JSON text of a map / list / set or of a field typed JSONB, or a null.
     */
    fun protobufValueToJson(value: AirbyteValueProtobuf): JsonNode =
        when (value.valueCase) {
            AirbyteValueProtobuf.ValueCase.JSON -> Jsons.readTree(value.json.toStringUtf8())
            AirbyteValueProtobuf.ValueCase.NULL,
            AirbyteValueProtobuf.ValueCase.VALUE_NOT_SET,
            null -> Jsons.nullNode()
            else ->
                when (val decoded: Any? = decoder.decode(value)) {
                    null -> Jsons.nullNode()
                    is String -> Jsons.textNode(decoded)
                    is Boolean -> Jsons.booleanNode(decoded)
                    is BigInteger -> JsonNodeFactory.instance.numberNode(decoded)
                    is BigDecimal -> JsonNodeFactory.instance.numberNode(decoded)
                    else -> Jsons.textNode(decoded.toString())
                }
        }

    fun decode(value: AirbyteValueProtobuf): Any? = decoder.decode(value)

    /**
     * The text a protobuf value carries on the wire: the string, the plain decimal digits of a
     * number, `true`/`false`, the JSON text of a JSON value, or null for a null.
     */
    fun wireText(value: AirbyteValueProtobuf): String? =
        when (val decoded: Any? = decoder.decode(value)) {
            null -> null
            is BigDecimal -> decoded.toPlainString()
            else -> decoded.toString()
        }

    /** `1E+5`, `-1E-7`: the notations a plain number must never be written in. */
    val SCIENTIFIC_NOTATION = Regex("""\d[eE][+-]?\d""")

    /**
     * Makes JSON values comparable across channels: every number becomes its plain decimal text
     * (the STDIO channel holds Jackson number nodes of various classes, the socket channels are
     * parsed from text), binary nodes become their base64 text (the STDIO channel holds `B` values
     * as binary nodes), and object keys are sorted (the protobuf channel orders fields
     * alphabetically).
     */
    fun normalize(node: JsonNode): JsonNode =
        when {
            node.isNumber ->
                Jsons.textNode(node.decimalValue().stripTrailingZeros().toPlainString())
            node.isBinary -> Jsons.textNode(node.asText())
            node.isObject -> {
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

    /** Every non-blank line of [bytes] (blank lines are the JSONL probe packets). */
    fun jsonlLines(bytes: ByteArray): List<String> =
        bytes.toString(Charsets.UTF_8).lineSequence().filter { it.isNotBlank() }.toList()

    /** Every non-blank line of [bytes] parsed as JSON. */
    fun parseJsonlMessages(bytes: ByteArray): List<JsonNode> =
        jsonlLines(bytes).map { Jsons.readTree(it) }

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
