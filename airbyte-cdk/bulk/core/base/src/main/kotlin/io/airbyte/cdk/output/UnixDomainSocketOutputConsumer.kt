package io.airbyte.cdk.output

import com.fasterxml.jackson.annotation.JsonInclude
import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.core.util.MinimalPrettyPrinter
import com.fasterxml.jackson.databind.DeserializationFeature
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.ObjectWriter
import com.fasterxml.jackson.databind.SequenceWriter
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.dataformat.smile.SmileFactory
import com.fasterxml.jackson.dataformat.smile.databind.SmileMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.afterburner.AfterburnerModule
import com.fasterxml.jackson.module.kotlin.KotlinModule
import com.fasterxml.jackson.module.kotlin.kotlinModule
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.BufferedOutputStream
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.PrintStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.Channels
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.time.Clock

private const val SOCKET_NAME_TEMPLATE = "ab_socket_%d"
private const val SOCKET_FULL_PATH = "/var/run/sockets/$SOCKET_NAME_TEMPLATE"
//private const val SOCKET_FULL_PATH = "/tmp/$SOCKET_NAME_TEMPLATE"
private val logger = KotlinLogging.logger {}

@Singleton
class UnixDomainSocketOutputConsumer(
    clock: Clock,
    stdout: PrintStream,
    @Value("\${$CONNECTOR_OUTPUT_PREFIX.buffer-byte-size-threshold-for-flush}")
    bufferByteSizeThresholdForFlush: Int,
) : StdoutOutputConsumer(stdout, clock, bufferByteSizeThresholdForFlush) {
    private var socketNum: Int = -1
    var sc: SocketChannel? = null
    var bufferedOutputStream: BufferedOutputStream? = null
    lateinit var ll: List<UnixDomainSocketOutputConsumer>
    public val SMILE_MAPPER: ObjectMapper = initSmileMapper();
    private val smileGenerator: JsonGenerator = SMILE_MAPPER.createGenerator(buffer)
    private val smileWriter: ObjectWriter? = SMILE_MAPPER.writerFor(AirbyteMessage::class.java).with(
        MinimalPrettyPrinter(System.lineSeparator()))
//    private lateinit var templateRecord: JsonNode


    fun initSmileMapper(): ObjectMapper {
        return configure(SmileMapper())
    }

    fun configure(objectMapper: ObjectMapper): ObjectMapper {
        return objectMapper
            .registerModule(JavaTimeModule())
            .registerModule(AfterburnerModule())
            .registerModule(kotlinModule())
            .configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
            .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false)
            .setSerializationInclusion(JsonInclude.Include.NON_NULL)
    }

    fun setSocketNum(num: Int) {
        socketNum = num
    }

    override fun accept(airbyteMessage: AirbyteMessage) {
        if (airbyteMessage.type == AirbyteMessage.Type.RECORD) {
            sc ?: let {
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
                logger.info { "Source : Server socket bound at ${socketFile.absolutePath}" }
                sc = serverSocketChannel.accept()

                bufferedOutputStream = Channels.newOutputStream(sc).buffered()
            }
            val seqWriter = smileWriter!!.writeValues(bufferedOutputStream)
            seqWriter.write(airbyteMessage)
            bufferedOutputStream!!.flush()

        } else {
            super.accept(airbyteMessage)
        }
    }
    override fun withLockFlushRecord() {
        if (buffer.size() > 0) {
            val array: ByteArray = buffer.toByteArray()
            sc?.write(ByteBuffer.wrap(array).order(ByteOrder.LITTLE_ENDIAN))
            buffer.reset()
        }
    }

    override fun close() {
        super.close()
        sc?.close()
    }

    override fun getS(num: Int): List<OutputConsumer>? {
        synchronized(this) {
            if (!::ll.isInitialized) {
                ll = List(num) { index ->
                    val udsoc = UnixDomainSocketOutputConsumer(clock, stdout, bufferByteSizeThresholdForFlush)
                    udsoc.setSocketNum(index)
                    udsoc
                }
            }
        }
        return ll
    }
}
