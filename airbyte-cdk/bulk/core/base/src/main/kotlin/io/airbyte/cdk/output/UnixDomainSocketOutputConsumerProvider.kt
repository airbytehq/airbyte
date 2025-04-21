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
import com.google.flatbuffers.FlatBufferBuilder
import io.airbyte.cdk.output.UnixDomainSocketOutputConsumer.NamedNode
import io.airbyte.protocol.AirbyteRecord
import io.airbyte.protocol.AirbyteValue
import io.airbyte.protocol.Protocol
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import jakarta.inject.Singleton
import java.io.BufferedOutputStream
import java.io.File
import java.io.OutputStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder
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
import org.xerial.snappy.SnappyOutputStream

private val logger = KotlinLogging.logger {}

enum class SocketOutputFormat {
    JSONL,
    PROTOBUF,
    SMILE,
    DEVNULL,
    FLATBUFFERS,
}

interface SocketConfig {
    val numSockets: Int
    val bufferByteSize: Int
    val outputFormat: SocketOutputFormat
    val devNullAfterSerialization: Boolean
    val inputChannelCapacity: Int
    val devNullBeforePosting: Boolean
    val writeAsync: Boolean
    val skipJsonNodeAndUseFakeRecord: Boolean
    val sharedInputChannel: Boolean
    val socketPrefix: String
    val useSnappy: Boolean
    val useFlow: Boolean
}

data class FlatBufferResult(
    val fbBuilder: FlatBufferBuilder = FlatBufferBuilder(),
    var fbDataVector: Int = -1,
    var fbDataTypeVector: Int = -1,
) {
    fun finish(namespace: String, streamName: String) {
        val namespaceOffset = fbBuilder.createString(namespace)
        val nameOffset = fbBuilder.createString(streamName)

        io.airbyte.protocol.AirbyteRecordMessage.startAirbyteRecordMessage(fbBuilder)
        io.airbyte.protocol.AirbyteRecordMessage.addStreamNamespace(
            fbBuilder,
            namespaceOffset
        )
        io.airbyte.protocol.AirbyteRecordMessage.addStreamName(fbBuilder, nameOffset)
        io.airbyte.protocol.AirbyteRecordMessage.addDataType(
            fbBuilder,
            fbDataTypeVector
        )
        io.airbyte.protocol.AirbyteRecordMessage.addData(fbBuilder, fbDataVector)
        io.airbyte.protocol.AirbyteRecordMessage.addEmittedAt(fbBuilder, System.currentTimeMillis())
        val root =
            io.airbyte.protocol.AirbyteRecordMessage.endAirbyteRecordMessage(fbBuilder)
        fbBuilder.finish(root)
    }

    fun clear() {
        fbDataVector = -1
        fbDataTypeVector = -1
        fbBuilder.clear()
    }
}

@Singleton
class UnixDomainSocketOutputConsumerProvider(
    clock: Clock,
    val configuration: SocketConfig,
) : AutoCloseable {
    private val numSockets = configuration.numSockets
    private val bufferByteSize = configuration.bufferByteSize
    private val outputFormat: SocketOutputFormat = configuration.outputFormat

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
                        "${configuration.socketPrefix}${socketNum}",
                        clock,
                        bufferByteSize,
                        outputFormat,
                        configuration.devNullAfterSerialization,
                        configuration.devNullBeforePosting,
                        configuration.writeAsync,
                        configuration.skipJsonNodeAndUseFakeRecord,
                        it,
                        if (configuration.useFlow) {
                            if (configuration.sharedInputChannel) {
                                it.receiveAsFlow()
                            } else {
                                it.consumeAsFlow()
                            }
                        } else {
                            null
                        },
                        configuration.useSnappy
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
                .let {
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
    socketPath: String,
    private val clock: Clock,
    bufferSize: Int = DEFAULT_BUFFER_SIZE,
    private val outputFormat: SocketOutputFormat,
    devNullAfterSerialization: Boolean = false,
    private val devNullBeforePosting: Boolean = false,
    private val writeAsync: Boolean,
    private val fakeRecord: Boolean,
    private val outputChannel: Channel<NamedNode>,
    private val inputFlow: Flow<NamedNode>? = null,
    private val useSnappy: Boolean
) : AutoCloseable {
    private val socketChannel: SocketChannel
    private val bufferedOutputStream: OutputStream
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
        val recordMessage: AirbyteRecord.AirbyteRecordMessage?,
        val fbBuffer: ByteArray? = null,
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
                DevNullOutputStream()
            } else {
                if (useSnappy) {
                    SnappyOutputStream(Channels.newOutputStream(socketChannel), bufferSize)
                } else {
                    Channels.newOutputStream(socketChannel).buffered(bufferSize)
                }
            }

        writer = writerForMapper()
    }

    private fun writerForMapper(): SequenceWriter {
        return if (outputFormat == SocketOutputFormat.JSONL) {
                OBJECT_MAPPER.writerFor(AirbyteMessage::class.java)
                    .with(MinimalPrettyPrinter(System.lineSeparator()))
            } else {
                SMILE_MAPPER.writerFor(AirbyteMessage::class.java)
            }
            .writeValues(bufferedOutputStream)
    }

    private val messageBuilder = if (outputFormat == SocketOutputFormat.PROTOBUF) {
        Protocol.AirbyteMessage.newBuilder()
            .setType(Protocol.AirbyteMessageType.RECORD)
    } else { null }

    fun accept(recordData: ObjectNode, recordMessage:  AirbyteRecord.AirbyteRecordMessage?, fbBuffer: ByteArray?,
               namespace: String, streamName: String, fbResult: FlatBufferResult? = null) {
        if (outputFormat == SocketOutputFormat.DEVNULL) {
            return
        }

        if (outputFormat == SocketOutputFormat.PROTOBUF) {
            val pMessage = messageBuilder!!
                .setRecord(recordMessage)
                .build()
            pMessage.writeDelimitedTo(bufferedOutputStream)
            messageBuilder.clear()
        } else if (outputFormat == SocketOutputFormat.FLATBUFFERS) {
            if (fbResult != null) {
                fbResult.finish(namespace, streamName)
                val buffer = fbResult.fbBuilder.dataBuffer()
                bufferedOutputStream.write(
                    ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN)
                        .putInt(buffer.remaining()).array()
                )
                bufferedOutputStream.write(
                    buffer.array(),
                    buffer.position(),
                    buffer.remaining()
                )
                fbResult.clear()
            } else {
                bufferedOutputStream.write(
                    ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(fbBuffer!!.size)
                        .array()
                )
                bufferedOutputStream.write(fbBuffer)
            }
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
                                 fbResult: FlatBufferResult,
                                 namespace: String,
                                 streamName: String
    ) {
        if (!writeAsync && outputFormat == SocketOutputFormat.FLATBUFFERS) {
            accept(recordData, null, null, namespace, streamName, fbResult)
            fbResult.fbBuilder.clear()
            return
        }

        val fbBuffer = if (outputFormat == SocketOutputFormat.PROTOBUF) {
            recordBuilder
                .setNamespace(namespace)
                .setStream(streamName)
                .setEmittedAt(clock.millis())
            null
        } else if (outputFormat == SocketOutputFormat.FLATBUFFERS) {
            fbResult.finish(namespace, streamName)
            fbResult.fbBuilder.sizedByteArray().also {
                fbResult.clear()
            }
        } else {
            null
        }

        val abMessage = if (outputFormat == SocketOutputFormat.PROTOBUF) {
            recordBuilder.build()
        } else {
            null
        }


        if (!writeAsync) {
            accept(recordData, recordBuilder.build(),null, namespace, streamName)
            return
        }

        val namedNode = NamedNode(namespace, streamName, recordData, abMessage, fbBuffer)
        if (devNullBeforePosting) {
            return
        }
        outputChannel.send(namedNode)
    }

    suspend fun writeToSocketUntilComplete() {
        if (inputFlow != null) {
            inputFlow.collect { (namespace, name, recordData, recordMessage, fbBuffer) ->
                accept(recordData, recordMessage, fbBuffer, namespace, name)
            }
        } else {
            for (namedNode in outputChannel) {
                accept(
                    namedNode.recordData,
                    namedNode.recordMessage,
                    namedNode.fbBuffer,
                    namedNode.namespace,
                    namedNode.streamName
                )
            }
        }
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
