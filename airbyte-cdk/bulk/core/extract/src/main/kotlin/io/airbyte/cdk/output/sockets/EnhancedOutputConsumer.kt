package io.airbyte.cdk.output.sockets

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.protobuf.kotlin.toByteString
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
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import java.math.BigDecimal
import java.net.URL
import java.nio.ByteBuffer
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
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
        is NullCodec, -> NullProtoEncoder
        is BinaryCodec, -> BinaryProtoEncoder
        is BigDecimalCodec, -> BigDecimalProtoEncoder
        is BigDecimalIntegerCodec, -> BigDecimalProtoEncoder // TODO: check can convert to exact integer
        is ShortCodec, -> ShortProtoEncoder
        is ByteCodec, -> ByteProtoEncoder
        is DoubleCodec, -> DoubleProtoEncoder
        is JsonBytesCodec, -> BinaryProtoEncoder
        is JsonStringCodec, -> TextProtoEncoder
        is UrlCodec, -> UrlProtoEncoder
        is LocalDateCodec, -> LocalDateProtoEncoder
        is LocalTimeCodec, -> LocalTimeProtoEncoder
        is LocalDateTimeCodec, -> LocalDateTimeProtoEncoder
        is OffsetTimeCodec, -> OffsetTimeProtoEncoder
        is ArrayEncoder<*>, -> AnyProtoEncoder
        else -> AnyProtoEncoder
    } as ProtoEncoder<T>
}


fun interface ProtoEncoder<T> {
    fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: T): AirbyteRecordMessage.AirbyteValueProtobuf.Builder
}

data object OffsetTimeProtoEncoder : ProtoEncoder<OffsetTime> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: OffsetTime): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setString(decoded.format(OffsetTimeCodec.formatter))
}

data object LocalDateTimeProtoEncoder : ProtoEncoder<LocalDateTime> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: LocalDateTime): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setString(decoded.format(LocalDateTimeCodec.formatter))
}

data object LocalTimeProtoEncoder : ProtoEncoder<LocalTime> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: LocalTime): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setString(decoded.format(LocalTimeCodec.formatter))
}

data object LocalDateProtoEncoder : ProtoEncoder<LocalDate> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: LocalDate): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setString(decoded.format(LocalDateCodec.formatter))
}

data object UrlProtoEncoder : ProtoEncoder<URL> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: URL): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setString(decoded.toExternalForm())
}

data object DoubleProtoEncoder : ProtoEncoder<Double> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: Double): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setNumber(decoded)
}

data object ByteProtoEncoder : ProtoEncoder<Byte> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: Byte): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setInteger(decoded.toLong())
}


data object BinaryProtoEncoder : ProtoEncoder<ByteBuffer> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: ByteBuffer): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setStringBytes(decoded.toByteString()) // TODO: check here. Need base64 encoded?
}

data object ShortProtoEncoder : ProtoEncoder<Short> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: Short): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setInteger(decoded.toLong())
}

data object BigDecimalProtoEncoder : ProtoEncoder<BigDecimal> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: BigDecimal): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setBigDecimal(decoded.toPlainString()) // TODO: check here. why string?
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

data object NullProtoEncoder : ProtoEncoder<Boolean> {
    override fun encode(builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder, decoded: Boolean): AirbyteRecordMessage.AirbyteValueProtobuf.Builder =
        builder.setIsNull(decoded)
}

typealias AnyProtoEncoder = TextProtoEncoder
fun InternalRow.toProto(recordMessageBuilder:  AirbyteRecordMessageProtobuf.Builder, valueVBuilder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder): AirbyteRecordMessageProtobuf.Builder {
    return recordMessageBuilder
        .apply {
            this@toProto.toSortedMap().onEachIndexed { index, entry ->
                setData(index,
                    entry.value.jsonEncoder.toProto().encode(valueVBuilder, entry.value.value!!))
                setData(index, NullProtoEncoder.encode(valueVBuilder, entry.value.value == null))
            }
/*
            for ((_, value) in this@toProto.toSortedMap()) {

                addData(value.jsonEncoder.toProto().encode(
                    valueVBuilder,
                    value.value!!))
            }
*/
        }
//        .build()
}



