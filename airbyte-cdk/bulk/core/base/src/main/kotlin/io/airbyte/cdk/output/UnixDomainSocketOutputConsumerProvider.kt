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
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.BufferedOutputStream
import java.io.File
import java.io.OutputStream
import java.io.PrintStream
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
   private const val SOCKET_FULL_PATH = "/var/run/sockets/$SOCKET_NAME_TEMPLATE"
// private const val SOCKET_FULL_PATH = "/Users/jschmidt/.sockets/$SOCKET_NAME_TEMPLATE"
//private const val SOCKET_FULL_PATH = "/tmp/$SOCKET_NAME_TEMPLATE"
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
@Secondary
class DefaultSocketConfig: SocketConfig {
    override val numSockets: Int = 1
    override val bufferByteSize: Int = 8 * 1024
    override val outputFormat: String = "jsonl"
    override val devNullAfterSerialization: Boolean = false
    override val inputChannelCapacity: Int = 20_000
    override val devNullBeforePosting: Boolean = false
    override val writeAsync: Boolean = false
    override val skipJsonNodeAndUseFakeRecord: Boolean = false
    override val sharedInputChannel: Boolean = false
}

@Singleton
class UnixDomainSocketOutputConsumerProvider(
    clock: Clock,
    stdout: PrintStream,
    @Value("\${$CONNECTOR_OUTPUT_PREFIX.buffer-byte-size-threshold-for-flush:4096}")
    bufferByteSizeThresholdForFlush: Int,
    val configuration: SocketConfig,
) : StdoutOutputConsumer(stdout, clock, bufferByteSizeThresholdForFlush) {
    val numSockets = configuration.numSockets
    val bufferByteSize = configuration.bufferByteSize
    val outputFormat: String = configuration.outputFormat

    private val sharedInputChannel: Channel<NamedNode> = Channel(configuration.inputChannelCapacity)

    private val socketConsumers = (0 until numSockets).map { socketNum ->
        if (configuration.sharedInputChannel) {
            sharedInputChannel
        } else {
            Channel(configuration.inputChannelCapacity)
        }.let {
            UnixDomainSocketOutputConsumer(
                socketNum,
                bufferByteSize,
                outputFormat,
                clock,
                stdout,
                bufferByteSizeThresholdForFlush,
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
        super.close()
        socketConsumers.forEach { it.close() }
    }

    override fun getNextFreeSocketConsumer(part: Int): UnixDomainSocketOutputConsumer {
        if (configuration.writeAsync) {
            return socketConsumers[part % socketConsumers.size]
        }

        synchronized(this) {
            return socketConsumers.first { it.busy.not() }.use { it.busy = true; it }
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
            ioScope.launch {
                socketConsumer.readSocketUntilComplete()
            }
        }
    }
}

class DevNullOutputStream: OutputStream() {
    override fun write(b: Int) {
        // No-op
    }

    override fun write(b: ByteArray, off: Int, len: Int) {
        // No-op
    }
}

class UnixDomainSocketOutputConsumer(
    val socketNum: Int,
    bufferSize: Int = DEFAULT_BUFFER_SIZE,
    val outputFormat: String,
    clock: Clock,
    stdout: PrintStream,
    bufferByteSizeThresholdForFlush: Int,
    val devNullAfterSerialization: Boolean = false,
    val devNullBeforePosting: Boolean = false,
    private val writeAsync: Boolean,
    private val fakeRecord: Boolean,
    private val outputChannel: Channel<NamedNode>,
    private val inputFlow: Flow<NamedNode>,
): StdoutOutputConsumer(stdout, clock, bufferByteSizeThresholdForFlush) {
    private val socketChannel: SocketChannel
    private val bufferedOutputStream: BufferedOutputStream
    private var writer: SequenceWriter
    private var numRecords: Int = 0
    var busy: Boolean = false

    val fakeRecordJson = """{"id":1,"age":50,"name":"Tomoko","email":"corrections1854+2@live.com","title":"Prof.","gender":"Female","height":1.53,"weight":61,"language":"Czech","global_id":13679213,"telephone":"357-652-0612","blood_type":"O+","created_at":"2009-02-27T13:44:37z","occupation":"MachineSetter","updated_at":"2009-07-12T16:12:23z","nationality":"Cameroonian","academic_degree":"Bachelor"}""".toByteArray(charset = Charsets.UTF_8)

    data class NamedNode(
        val namespace: String,
        val streamName: String,
        val recordData: ObjectNode
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
        bufferedOutputStream = if (devNullAfterSerialization) {
            DevNullOutputStream().buffered(bufferSize)
        } else {
            Channels.newOutputStream(socketChannel).buffered(bufferSize)
        }

        writer = writerForMapper()
    }

    private fun writerForMapper(): SequenceWriter {
        return if (outputFormat == "json") {
            OBJECT_MAPPER.writerFor(AirbyteMessage::class.java).with(
                MinimalPrettyPrinter(System.lineSeparator())
            )
        } else {
            SMILE_MAPPER.writerFor(AirbyteMessage::class.java)
        }.writeValues(bufferedOutputStream)
    }

    fun accept(recordData: ObjectNode, namespace: String, streamName: String) {
        if (outputFormat == "devnull") {
            return
        }

        if (outputFormat in listOf("proto", "protobuf")) {
            val pMessage: Protocol.AirbyteMessage? = Protocol.AirbyteMessage.newBuilder()
                .setType(Protocol.AirbyteMessageType.RECORD)
                .setRecord(
                    AirbyteRecord.AirbyteRecordMessage.newBuilder()
                        .setStream(streamName)
                        .setNamespace(namespace)
                        .setData(ByteString.copyFrom(
                            if (fakeRecord) { fakeRecordJson } else { Jsons.writeValueAsBytes(recordData) }
                        ))
                        .setEmittedAt(clock.millis())
                        .build()
                )
                .build()
            pMessage?.writeDelimitedTo(bufferedOutputStream)
        } else {
            val airbyteMessage = AirbyteMessage()
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


    suspend fun acceptAsyncMaybe(recordData: ObjectNode, namespace: String, streamName: String) {
        if (!writeAsync) {
            accept(recordData, namespace, streamName)
            return
        }

        val namedNode = NamedNode(namespace, streamName, recordData)
        if (devNullBeforePosting) {
            return
        }
        outputChannel.send(namedNode)
    }

    suspend fun readSocketUntilComplete() {
        inputFlow.collect { (namespace, name, recordData) ->
            accept(recordData, namespace, name)
        }
    }

    override fun accept(airbyteMessage: AirbyteMessage) {
        throw UnsupportedOperationException("Not supported")
    }
}
