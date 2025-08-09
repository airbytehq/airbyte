/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

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
import io.airbyte.cdk.discover.FieldOrMetaField
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

// A value of a field along with its encoder
class FieldValueEncoder<R>(val fieldValue: R?, val jsonEncoder: JsonEncoder<in R>) {
    fun encode(): JsonNode {
        return fieldValue?.let { jsonEncoder.encode(it) } ?: NullCodec.encode(null)
    }
}

// A native jvm encoding of a database row, which can then be encoded to the desired output format
// (json or protobuf)
typealias NativeRecordPayload = MutableMap<String, FieldValueEncoder<*>>

fun NativeRecordPayload.toJson(parentNode: ObjectNode = Jsons.objectNode()): ObjectNode {
    for ((columnId, value) in this) {
        parentNode.set<JsonNode>(columnId, value.encode())
    }
    return parentNode
}

fun <T> JsonEncoder<T>.toProtobufEncoder(): ProtoEncoder<*> {
    return when (this) {
        is LongCodec, -> longProtoEncoder
        is IntCodec, -> intProtoEncoder
        is TextCodec, -> textProtoEncoder
        is BooleanCodec, -> booleanProtoEncoder
        is OffsetDateTimeCodec, -> offsetDateTimeProtoEncoder
        is FloatCodec, -> floatProtoEncoder
        is NullCodec, -> nullProtoEncoder
        is BinaryCodec, -> binaryProtoEncoder
        is BigDecimalCodec, -> bigDecimalProtoEncoder
        is BigDecimalIntegerCodec, ->
            bigDecimalProtoEncoder // TODO: check can convert to exact integer
        is ShortCodec, -> shortProtoEncoder
        is ByteCodec, -> byteProtoEncoder
        is DoubleCodec, -> doubleProtoEncoder
        is JsonBytesCodec, -> binaryProtoEncoder
        is JsonStringCodec, -> textProtoEncoder
        is UrlCodec, -> urlProtoEncoder
        is LocalDateCodec, -> localDateProtoEncoder
        is LocalTimeCodec, -> localTimeProtoEncoder
        is LocalDateTimeCodec, -> localDateTimeProtoEncoder
        is OffsetTimeCodec, -> offsetTimeProtoEncoder
        is ArrayEncoder<*>, -> anyProtoEncoder
        else -> anyProtoEncoder
    }
}

fun interface ProtoEncoder<T> {
    fun encode(
        builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder,
        decoded: T
    ): AirbyteRecordMessage.AirbyteValueProtobuf.Builder
}

/**
 * Generates a ProtoEncoder for a specific type T.
 *
 * @param setValue A lambda function that sets the value in the builder for the given type T.
 * @return A ProtoEncoder instance that encodes values of type T into AirbyteValueProtobuf.
 */
private inline fun <T> generateProtoEncoder(
    crossinline setValue:
        (
            AirbyteRecordMessage.AirbyteValueProtobuf.Builder,
            T
        ) -> AirbyteRecordMessage.AirbyteValueProtobuf.Builder
): ProtoEncoder<T> =
    object : ProtoEncoder<T> {
        override fun encode(
            builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder,
            decoded: T
        ): AirbyteRecordMessage.AirbyteValueProtobuf.Builder = setValue(builder, decoded)
    }

val offsetTimeProtoEncoder =
    generateProtoEncoder<OffsetTime> { builder, value ->
        builder.setString(value.format(OffsetTimeCodec.formatter))
    }
val localDateTimeProtoEncoder =
    generateProtoEncoder<LocalDateTime> { builder, value ->
        builder.setString(value.format(LocalDateTimeCodec.formatter))
    }
val localTimeProtoEncoder =
    generateProtoEncoder<LocalTime> { builder, time ->
        builder.setString(time.format(LocalTimeCodec.formatter))
    }
val localDateProtoEncoder =
    generateProtoEncoder<LocalDate> { builder, date ->
        builder.setString(date.format(LocalDateCodec.formatter))
    }
val urlProtoEncoder =
    generateProtoEncoder<URL> { builder, url -> builder.setString(url.toExternalForm()) }
val doubleProtoEncoder = generateProtoEncoder<Double> { builder, value -> builder.setNumber(value) }
val byteProtoEncoder =
    generateProtoEncoder<Byte> { builder, value -> builder.setInteger(value.toLong()) }
val binaryProtoEncoder =
    generateProtoEncoder<ByteBuffer> { builder, decoded ->
        builder.setStringBytes(decoded.toByteString()) // TODO: check here. Need base64 encoded?
    }
val shortProtoEncoder =
    generateProtoEncoder<Short> { builder, value -> builder.setInteger(value.toLong()) }
val bigDecimalProtoEncoder =
    generateProtoEncoder<BigDecimal> { builder, decoded ->
        builder.setBigDecimal(decoded.toPlainString()) // TODO: check here. why string?
    }
val longProtoEncoder = generateProtoEncoder<Long> { builder, value -> builder.setInteger(value) }
val textProtoEncoder = generateProtoEncoder<String> { builder, value -> builder.setString(value) }
val intProtoEncoder =
    generateProtoEncoder<Int> { builder, value -> builder.setInteger(value.toLong()) }
val booleanProtoEncoder =
    generateProtoEncoder<Boolean> { builder, value -> builder.setBoolean(value) }
val offsetDateTimeProtoEncoder =
    generateProtoEncoder<OffsetDateTime> { builder, decoded ->
        builder.setTimestampWithTimezone(decoded.format(OffsetDateTimeCodec.formatter))
    }
val floatProtoEncoder =
    generateProtoEncoder<Float> { builder, decoded -> builder.setNumber(decoded.toDouble()) }

val nullProtoEncoder = generateProtoEncoder<Any?> { builder, _ -> builder.setIsNull(true) }
val anyProtoEncoder = textProtoEncoder
// typealias AnyProtoEncoder = TextProtoEncoder

fun NativeRecordPayload.toProtobuf(
    schema: Set<FieldOrMetaField>,
    recordMessageBuilder: AirbyteRecordMessageProtobuf.Builder,
    valueBuilder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder
): AirbyteRecordMessageProtobuf.Builder {
    return recordMessageBuilder.apply {
        schema
            .sortedBy { it.id }
            .forEachIndexed { index, field ->
                // Protobuf does not have field names, so we use a sorted order of fields
                // So for destination to know which fields it is, we order the fields alphabetically
                // to make sure that the order is consistent.
                this@toProtobuf[field.id]?.let { value ->
                    @Suppress("UNCHECKED_CAST")
                    setData(
                        index,
                        value.fieldValue?.let {
                            (value.jsonEncoder.toProtobufEncoder() as ProtoEncoder<Any>).encode(
                                valueBuilder.clear(),
                                value.fieldValue
                            )
                        }
                            ?: nullProtoEncoder.encode(valueBuilder.clear(), null)
                    )
                }
            }
    }
}
