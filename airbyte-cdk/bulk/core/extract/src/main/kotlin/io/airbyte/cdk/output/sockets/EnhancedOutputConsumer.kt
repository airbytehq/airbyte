package io.airbyte.cdk.output.sockets

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.SequenceWriter
import com.fasterxml.jackson.databind.node.NullNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.ArrayEncoder
import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BigDecimalIntegerCodec
import io.airbyte.cdk.data.BinaryCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.ByteCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.FloatCodec
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.JsonBytesCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.ShortCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.data.UrlCodec
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.ByteArrayOutputStream
import java.time.Clock
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter


data class FieldValueEncoder(val value: Any?, val jsonEncoder: JsonEncoder<Any>)
typealias InternalRow = MutableMap<String, FieldValueEncoder>

fun InternalRow.toJson(parentNode: ObjectNode = Jsons.objectNode()): ObjectNode {
    for ((columnId, value) in this) {
        val encodedValue = value.jsonEncoder.encode(value.value!!)
        parentNode.set<JsonNode>(columnId, encodedValue)
    }
    return parentNode
}

@Suppress("UNCHECKED_CAST")
fun <T> JsonEncoder<T>.toProto(): ProtoEncoder<T> {
    return when (this) {
        is LongCodec, -> LongProtoEncoder
        is IntCodec, -> IntProtoEncoder
        is TextCodec, -> TextProtoEncoder
        is BooleanCodec, -> BooleanProtoEncoder
        is OffsetDateTimeCodec, -> OffsetDateTimeProtoEncoder
        is FloatCodec, -> FloatProtoEncoder
        is BinaryCodec,
        is BigDecimalCodec,
        is BigDecimalIntegerCodec,
        is ShortCodec,
        is ByteCodec,
        is DoubleCodec,
        is JsonBytesCodec,
        is JsonStringCodec,
        is UrlCodec,
        is LocalDateCodec,
        is LocalTimeCodec,
        is LocalDateTimeCodec,
        is OffsetTimeCodec,
        is NullCodec,
        is ArrayEncoder<*>, -> AnyProtoEncoder

        else -> AnyProtoEncoder
    } as ProtoEncoder<T>
}


fun interface ProtoEncoder<T> {
    fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: T): AirbyteRecordMessage.AirbyteValueProtobuf.Builder
}

data object LongProtoEncoder : ProtoEncoder<Long> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: Long): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setInteger(decoded)
}

data object TextProtoEncoder : ProtoEncoder<String> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: String): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setString(decoded)
}


data object IntProtoEncoder : ProtoEncoder<Int> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: Int): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setInteger(decoded.toLong())
}

data object BooleanProtoEncoder : ProtoEncoder<Boolean> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: Boolean): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setBoolean(decoded)
}

data object OffsetDateTimeProtoEncoder: ProtoEncoder<OffsetDateTime> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: OffsetDateTime): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setTimestampWithTimezone(decoded.format(formatter))

    const val PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX"
    val formatter: DateTimeFormatter = DateTimeFormatter.ofPattern(PATTERN)
}

data object FloatProtoEncoder: ProtoEncoder<Float> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: Float): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setNumber(decoded.toDouble())
}

typealias AnyProtoEncoder = TextProtoEncoder

fun InternalRow.toProto(recordMessageBuilder:  AirbyteRecordMessageProtobuf.Builder): AirbyteRecordMessageProtobuf.Builder =
    recordMessageBuilder
        .apply {
            for ((_, value) in this@toProto.toSortedMap()) {
                addData(value.jsonEncoder.toProto().encode(
                    AirbyteRecordMessage.AirbyteValueProtobuf.newBuilder(),
                    value.value!!))
            }
        }



class ProtoRecordOutputConsumer(
    private val socket: SocketWrapper,
    private val clock: Clock,
    val bufferByteSizeThresholdForFlush: Int,
): OutputConsumer(clock)
{
    private val log = KotlinLogging.logger {}
    private val buffer = ByteArrayOutputStream()

    override fun accept(airbyteMessage: io.airbyte.protocol.models.v0.AirbyteMessage) {
        // This method effectively println's its JSON-serialized argument.
        // Using println is not particularly efficient, however.
        // To improve performance, this method accumulates RECORD messages into a buffer
        // before writing them to standard output in a batch.
        if (airbyteMessage.type == io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD) {
            // RECORD messages undergo a different serialization scheme.
            //accept(airbyteMessage.record)
            //no-op
        } else {
            synchronized(this) {
                val b = ByteArrayOutputStream()
                val sequenceWriter: SequenceWriter = Jsons.writer().writeValues(b)
                sequenceWriter.write(airbyteMessage)
                sequenceWriter.flush()

                val pm = AirbyteMessage.AirbyteMessageProtobuf.newBuilder()
                    .setAirbyteProtocolMessage(String(b.toByteArray()))
                    .build()
                pm.writeDelimitedTo(buffer)

//                // Write a newline character to the buffer if it's not empty.
//                withLockMaybeWriteNewline()
//                // Non-RECORD AirbyteMessage instances are serialized and written to the buffer
//                // using standard jackson object mapping facilities.
//                sequenceWriter.write(airbyteMessage)
//                sequenceWriter.flush()
//                // Such messages don't linger in the buffer, they are flushed to stdout immediately,
//                // along with whatever might have already been lingering inside.
//                // This prints a newline after the message.
                log.info { "AirbyteMessage sent over SOCKET: ${String(b.toByteArray())}" }
                withLockFlush()
            }
        }
    }
    fun accept(airbyteProtoMessage: AirbyteMessage.AirbyteMessageProtobuf) {
        synchronized(this) {
            airbyteProtoMessage.writeDelimitedTo(buffer)
            if (buffer.size() >= bufferByteSizeThresholdForFlush) {
                withLockFlush()
            }

        }
     }

    private fun withLockFlush() {
        if (buffer.size() > 0) {
            buffer.writeTo(socket.outputStream)
            socket.outputStream?.write(System.lineSeparator().toByteArray())
//            stdout.println(buffer.toString(Charsets.UTF_8))
//            stdout.flush()
            buffer.reset()
        }
    }

    override fun close() {
        TODO("Not yet implemented")
    }
}
