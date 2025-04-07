package io.airbyte.cdk.output

import com.fasterxml.jackson.core.JsonGenerator
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.SequenceWriter
import com.fasterxml.jackson.databind.node.ObjectNode
import com.fasterxml.jackson.dataformat.smile.SmileFactory
import com.fasterxml.jackson.dataformat.smile.databind.SmileMapper
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule
import com.fasterxml.jackson.module.afterburner.AfterburnerModule
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Value
import jakarta.inject.Singleton
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.PrintStream
import java.net.StandardProtocolFamily
import java.net.UnixDomainSocketAddress
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.channels.ServerSocketChannel
import java.nio.channels.SocketChannel
import java.time.Clock

private const val SOCKET_NAME_TEMPLATE = "ab_socket_%d"
private const val SOCKET_FULL_PATH = "/var/run/sockets/$SOCKET_NAME_TEMPLATE"
//private const val SOCKET_FULL_PATH = "/tmp/$SOCKET_NAME_TEMPLATE"
private val logger = KotlinLogging.logger {}
public val SMILE_MAPPER: ObjectMapper = initSmileMapper();

fun initSmileMapper(): ObjectMapper {
    return configure(SmileMapper())
}

fun configure(objectMapper: ObjectMapper): ObjectMapper {
    return objectMapper
        .configure(JsonGenerator.Feature.WRITE_BIGDECIMAL_AS_PLAIN, true)
        .registerModule(JavaTimeModule())
        .registerModule(AfterburnerModule())


}

@Singleton
class UnixDomainSocketOutputConsumer(
    clock: Clock,
    stdout: PrintStream,
    @Value("\${$CONNECTOR_OUTPUT_PREFIX.buffer-byte-size-threshold-for-flush}")
    bufferByteSizeThresholdForFlush: Int,
) : StdoutOutputConsumer(stdout, clock, bufferByteSizeThresholdForFlush) {
    private var socketNum: Int = -1
    var sc: SocketChannel? = null
    lateinit var ll: List<UnixDomainSocketOutputConsumer>
    private val smileGenerator: JsonGenerator = SMILE_MAPPER.createGenerator(buffer)
//    private val smileSequenceWriter: SequenceWriter = SMILE_MAPPER.writer().writeValues(smileGenerator)
    private lateinit var templateRecord: JsonNode

    fun setSocketNum(num: Int) {
        socketNum = num
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
        if (::templateRecord.isInitialized.not()) {
            val template: RecordTemplate = getOrCreateRecordTemplate(record.stream, record.namespace)

            val tmplt = String(template.prefix + "{}".toByteArray() + template.suffix)

            templateRecord = Jsons.readTree(tmplt)
        }
        val rec = templateRecord.get("record") as ObjectNode
        rec.set<ObjectNode>("data", record.data)

//        val tb = ByteArrayOutputStream()
//        val gen = SMILE_MAPPER.createGenerator(tb)
//        Jsons.writeTree(gen, tt)

//        val rr = SMILE_MAPPER.readTree(tb.toByteArray())
//        val rr = SMILE_MAPPER.readerFor(AirbyteMessage::class.java).readTree(tb.toByteArray())
//        logger.info { rr }
//        assert(rr == tt)
//        synchronized(this) {
        // Write a newline character to the buffer if it's not empty.
//        withLockMaybeWriteNewline()
        // Write '{"type":"RECORD","record":{"namespace":"...","stream":"...","data":'.
//        buffer.write(template.prefix)
        // Serialize the record data ObjectNode to JSON, writing it to the buffer.
//        Jsons.writeTree(smileGenerator, record.data)

        Jsons.writeTree(smileGenerator, templateRecord)
        smileGenerator.flush()
        // If the record has a AirbyteRecordMessageMeta instance set,
        // write ',"meta":' followed by the serialized meta.
        /*val meta: AirbyteRecordMessageMeta? = record.meta
        if (meta != null) {
            buffer.write(metaPrefixBytes)
            smileSequenceWriter.write(meta)
            smileSequenceWriter.flush()
        }*/
        // Write ',"emitted_at":...}}'.
//        buffer.write(template.suffix)
        // Flush the buffer to stdout only once it has reached a certain size.
        // Flushing to stdout incurs some overhead (mutex, syscall, etc.)
        // which otherwise becomes very apparent when lots of tiny records are involved.
        if (buffer.size() >= bufferByteSizeThresholdForFlush) {
            withLockFlushRecord()
        }
//        }

    }
    override fun withLockFlushRecord() {
        synchronized(this) {
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
            }
        }
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
