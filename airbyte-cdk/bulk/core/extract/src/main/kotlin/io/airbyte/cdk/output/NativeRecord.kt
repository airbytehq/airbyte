/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.data.ArrayEncoder
import io.airbyte.cdk.data.BigDecimalIntegerCodec
import io.airbyte.cdk.data.ByteCodec
import io.airbyte.cdk.data.CdcOffsetDateTimeCodec
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.NullCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.UrlCodec
import io.airbyte.cdk.discover.DataOrMetaField
import io.airbyte.cdk.protocol.AirbyteValueProtobufEncoder
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.protobuf.AirbyteRecordMessage
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import java.math.BigDecimal
import java.net.URL
import java.time.OffsetDateTime

// A value of a field along with its encoder
class FieldValueEncoder<R>(val fieldValue: R?, val jsonEncoder: JsonEncoder<in R>) {
    fun encode(): JsonNode {
        return fieldValue?.let { jsonEncoder.encode(it) } ?: NullCodec.encode(null)
    }
}

// A native jvm encoding of a database row, which can then be encoded to the desired output format
// (json or protobuf)
typealias NativeRecordPayload = MutableMap<String, FieldValueEncoder<*>>

val encoder = AirbyteValueProtobufEncoder()

fun NativeRecordPayload.toJson(parentNode: ObjectNode = Jsons.objectNode()): ObjectNode {
    for ((columnId, value) in this) {
        parentNode.set<JsonNode>(columnId, value.encode())
    }
    return parentNode
}

/*interface ConnectorJsonEncoder {
    fun toProtobufEncoder(): ProtoEncoder<*>
}

fun <T> JsonEncoder<T>.toProtobufEncoder(): ProtoEncoder<*> {
    return when (this) {
        is ConnectorJsonEncoder -> toProtobufEncoder()
        is LongCodec, -> longProtoEncoder
        is IntCodec, -> intProtoEncoder
        is TextCodec, -> textProtoEncoder
        is BooleanCodec, -> booleanProtoEncoder
        is OffsetDateTimeCodec, -> offsetDateTimeProtoEncoder
        is FloatCodec, -> floatProtoEncoder
        is NullCodec, -> nullProtoEncoder
        is BinaryCodec, -> binaryProtoEncoder
        is BigDecimalCodec, -> bigDecimalProtoEncoder
        is BigDecimalIntegerCodec, -> bigDecimalProtoEncoder
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
        is ArrayEncoder<*>, -> arrayProtoEncoder
        else -> anyProtoEncoder
    }
}

fun interface ProtoEncoder<T> {
    fun encode(
        builder: AirbyteRecordMessage.AirbyteValueProtobuf.Builder,
        decoded: T
    ): AirbyteRecordMessage.AirbyteValueProtobuf.Builder
}*/

/**
 * Transforms a field value into a protobuf-compatible representation. Handles special conversions
 * for types that need preprocessing before protobuf encoding, such as ByteBuffer -> Base64 String,
 * BigDecimal -> BigInteger, URL -> String, etc.
 */
fun <R> valueForProtobufEncoding(fve: FieldValueEncoder<R>): Any? {
    return fve.fieldValue?.let { value ->
        when (fve.jsonEncoder) {
            is BigDecimalIntegerCodec -> (value as BigDecimal).toBigInteger()
            is ByteCodec -> (value as Byte).toLong()
            is UrlCodec -> (value as URL).toExternalForm()
            is CdcOffsetDateTimeCodec ->
                (value as OffsetDateTime).format(OffsetDateTimeCodec.formatter)
            is ArrayEncoder<*> -> fve.encode().toString()
            else -> value
        }
    }
}

fun NativeRecordPayload.toProtobuf(
    schema: Set<DataOrMetaField>,
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
                this@toProtobuf[field.id]?.let { fve ->
                    val decodedValueForProto = valueForProtobufEncoding(fve)
                    setData(
                        index,
                        encoder.encode(
                            decodedValueForProto,
                            field.type.airbyteSchemaType,
                            valueBuilder.clear()
                        )
                    )
                }
            }
    }
}
