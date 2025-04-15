/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.core.util.MinimalPrettyPrinter
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.SequenceWriter
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.dataformat.smile.databind.SmileMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.afterburner.AfterburnerModule
import com.fasterxml.jackson.module.kotlin.kotlinModule
import com.google.protobuf.ByteString
import io.airbyte.cdk.output.UnixDomainSocketOutputConsumer.NamedNode
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.AirbyteRecord
import io.airbyte.protocol.Protocol
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Secondary
import jakarta.inject.Singleton
import java.io.BufferedOutputStream
import java.io.File
import java.io.OutputStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.channels.Channels
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.time.Clock
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.consumeAsFlow
import kotlinx.coroutines.flow.receiveAsFlow
import kotlinx.coroutines.launch

private const val SOCKET_NAME_TEMPLATE = "ab_socket_%d"
///private const val SOCKET_FULL_PATH = "/var/run/sockets/$SOCKET_NAME_TEMPLATE"
private const val SOCKET_FULL_PATH = "/Users/jschmidt/.sockets/$SOCKET_NAME_TEMPLATE"
// private const val SOCKET_FULL_PATH = "/tmp/$SOCKET_NAME_TEMPLATE"
private val logger = KotlinLogging.logger {}

interface SocketConfig {
    val numSockets: Int
    val bufferByteSize: Int
    val outputFormat: String
    val devNullAfterSerialization: Boolean
    val inputChannelCapacity: Int
    val devNullBeforePosting: Boolean
    val writeAsync: Boolean
    val skipJsonNodeAndUseFakeRecord: Boolean
    val sharedInputChannel: Boolean
}

@Singleton
class UnixDomainSocketOutputConsumerProvider(
    clock: Clock,
    val configuration: SocketConfig,
) : AutoCloseable {
    private val numSockets = configuration.numSockets
    private val bufferByteSize = configuration.bufferByteSize
    private val outputFormat: String = configuration.outputFormat

    private val sharedInputChannel: Channel<NamedNode> = Channel(configuration.inputChannelCapacity)

    private val socketConsumers =
        (0 until numSockets).map { socketNum ->
            if (configuration.sharedInputChannel) {
                    sharedInputChannel
                } else {
                    Channel(configuration.inputChannelCapacity)
                }
                .let {
                    UnixDomainSocketOutputConsumer(
                        socketNum,
                        clock,
                        bufferByteSize,
                        outputFormat,
                        configuration.devNullAfterSerialization,
                        configuration.devNullBeforePosting,
                        configuration.writeAsync,
                        configuration.skipJsonNodeAndUseFakeRecord,
                        it,
                        if (configuration.sharedInputChannel) {
                            it.receiveAsFlow()
                        } else {
                            it.consumeAsFlow()
                        },
                    )
                }
        }

    override fun close() {
        socketConsumers.forEach { it.close() }
    }

    fun getNextFreeSocketConsumer(part: Int): UnixDomainSocketOutputConsumer {
        if (configuration.writeAsync) {
            return socketConsumers[part % socketConsumers.size]
        }

        synchronized(this) {
            return socketConsumers
                .first { it.busy.not() }
                .use {
                    it.busy = true
                    it
                }
        }
    }

    private val ioScope = CoroutineScope(Dispatchers.IO)

    suspend fun startAll() {
        if (!configuration.writeAsync) {
            return
        }

        socketConsumers.forEachIndexed { i, socketConsumer ->
            logger.info {
                "Starting socket consumer $i with capacity ${configuration.inputChannelCapacity} and buffer size ${configuration.bufferByteSize}"
            }
            ioScope.launch { socketConsumer.writeToSocketUntilComplete() }
        }
    }
}

class DevNullOutputStream : OutputStream() {
    override fun write(b: Int) {
        // No-op
    }

    override fun write(b: ByteArray, off: Int, len: Int) {
        // No-op
    }
}

class UnixDomainSocketOutputConsumer(
    socketNum: Int,
    private val clock: Clock,
    bufferSize: Int = DEFAULT_BUFFER_SIZE,
    private val outputFormat: String,
    devNullAfterSerialization: Boolean = false,
    private val devNullBeforePosting: Boolean = false,
    private val writeAsync: Boolean,
    private val fakeRecord: Boolean,
    private val outputChannel: Channel<NamedNode>,
    private val inputFlow: Flow<NamedNode>,
) : AutoCloseable {
    private val socketChannel: SocketChannel
    private val bufferedOutputStream: BufferedOutputStream
    private var writer: SequenceWriter
    private var numRecords: Int = 0
    var busy: Boolean = false

    private val fakeRecordJson =
        """{"id":1,"age":50,"name":"Tomoko","email":"corrections1854+2@live.com","title":"Prof.","gender":"Female","height":1.53,"weight":61,"language":"Czech","global_id":13679213,"telephone":"357-652-0612","blood_type":"O+","created_at":"2009-02-27T13:44:37z","occupation":"MachineSetter","updated_at":"2009-07-12T16:12:23z","nationality":"Cameroonian","academic_degree":"Bachelor"}""".toByteArray(
            charset = Charsets.UTF_8
        )

    data class NamedNode(
        val namespace: String,
        val streamName: String,
        val recordData: ObjectNode,
        val recordMessage: AirbyteRecord.AirbyteRecordMessage,
    )

    private fun configure(objectMapper: ObjectMapper): ObjectMapper {
        return objectMapper
            .registerModule(JavaTimeModule())
            .registerModule(AfterburnerModule())
            .registerModule(kotlinModule())
            .configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
            .setSerializationInclusion(JsonInclude.Include.NON_NULL)
    }

    private fun initSmileMapper(): ObjectMapper {
        return configure(SmileMapper())
    }

    private fun initJsonMapper(): ObjectMapper {
        return configure(ObjectMapper())
    }

    private val SMILE_MAPPER: ObjectMapper = initSmileMapper()
    private val OBJECT_MAPPER: ObjectMapper = initJsonMapper()

    init {
        val socketPath = String.format(SOCKET_FULL_PATH, socketNum)
        logger.info { "Using socket..." }
        val socketFile = File(socketPath)
        logger.info { "Socket File path $socketPath" }
        if (socketFile.exists()) {
            socketFile.delete()
        }
        val address = UnixDomainSocketAddress.of(socketFile.toPath())
        val serverSocketChannel: ServerSocketChannel =
            ServerSocketChannel.open(StandardProtocolFamily.UNIX)
        serverSocketChannel.bind(address)
        socketChannel = serverSocketChannel.accept()
        bufferedOutputStream =
            if (devNullAfterSerialization) {
                DevNullOutputStream().buffered(bufferSize)
            } else {
                Channels.newOutputStream(socketChannel).buffered(bufferSize)
            }

        writer = writerForMapper()
    }

    private fun writerForMapper(): SequenceWriter {
        return if (outputFormat == "json") {
                OBJECT_MAPPER.writerFor(AirbyteMessage::class.java)
                    .with(MinimalPrettyPrinter(System.lineSeparator()))
            } else {
                SMILE_MAPPER.writerFor(AirbyteMessage::class.java)
            }
            .writeValues(bufferedOutputStream)
    }

    val messageBuilder = Protocol.AirbyteMessage.newBuilder()
        .setType(Protocol.AirbyteMessageType.RECORD)

    fun accept(recordData: ObjectNode, recordMessage:  AirbyteRecord.AirbyteRecordMessage, namespace: String, streamName: String) {
        if (outputFormat == "devnull") {
            return
        }

        if (outputFormat in listOf("proto", "protobuf")) {
            val pMessage = messageBuilder
                .setRecord(recordMessage)
                .build()
            pMessage.writeDelimitedTo(bufferedOutputStream)
        } else {
            val airbyteMessage =
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.RECORD)
                    .withRecord(
                        AirbyteRecordMessage()
                            .withNamespace(namespace)
                            .withStream(streamName)
                            .withData(recordData)
                            .withEmittedAt(clock.millis())
                    )
            writer.write(airbyteMessage)
        }
        numRecords++
        if (numRecords == 100_000) {
            bufferedOutputStream.flush()
            numRecords = 0
        }
    }

    suspend fun acceptAsyncMaybe(recordData: ObjectNode,
                                 recordBuilder: AirbyteRecord.AirbyteRecordMessage.Builder,
                                 namespace: String,
                                 streamName: String
    ) {
        recordBuilder
            .setNamespace(namespace)
            .setStream(streamName)
            .setEmittedAt(clock.millis())

        if (!writeAsync) {
            accept(recordData, recordBuilder.build(), namespace, streamName)
            return
        }

        val namedNode = NamedNode(namespace, streamName, recordData, recordBuilder.build())
        if (devNullBeforePosting) {
            return
        }
        outputChannel.send(namedNode)
    }

    suspend fun writeToSocketUntilComplete() {
        inputFlow.collect { (namespace, name, recordData, recordMessage) -> accept(recordData, recordMessage, namespace, name) }
    }

    override fun close() {
        if (writeAsync) {
            outputChannel.close()
        } else {
            bufferedOutputStream.flush()
            bufferedOutputStream.close()
        }
    }
}
