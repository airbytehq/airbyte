/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import io.airbyte.cdk.data.AirbyteSchemaType
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
import io.airbyte.cdk.data.LeafAirbyteSchemaType
import io.airbyte.cdk.data.LocalDateCodec
import io.airbyte.cdk.data.LocalDateTimeCodec
import io.airbyte.cdk.data.LocalTimeCodec
import io.airbyte.cdk.data.LongCodec
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.ShortCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.data.UrlCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.protocol.AirbyteValueProtobufDecoder
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.net.URI
import java.net.URL
import java.nio.ByteBuffer
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory

class NativeRecordProtobufEncoderTest {
    private val protoDecoder = AirbyteValueProtobufDecoder()

    data class TestCase<T>(
        val value: T,
        val jsonEncoder: JsonEncoder<*>,
        val airbyteSchemaType: AirbyteSchemaType,
    ) {
        val asDecoderType: Any
            get() =
                when (value) {
                    is Short, -> value.toLong().toBigInteger()
                    is Int -> value.toBigInteger()
                    is Long -> value.toBigInteger()
                    is Float -> value.toDouble().toBigDecimal()
                    is BigDecimal -> if (value.scale() == 0) value.toBigInteger() else value
                    is URL -> value.toExternalForm()
                    is ByteBuffer ->
                        when (jsonEncoder) {
                            is JsonBytesCodec -> value.array().toString(Charsets.UTF_8)
                            else -> java.util.Base64.getEncoder().encodeToString(value.array())
                        }
                    is Byte -> value.toLong().toBigInteger()
                    is Double -> value.toBigDecimal()
                    else -> value!!
                }
    }

    val valBuilder = AirbyteValueProtobuf.newBuilder()
    val protoBuilder =
        AirbyteRecordMessageProtobuf.newBuilder().also { it.addData(0, valBuilder.clear()) }

    fun fieldOf(airbyteSchemaType: AirbyteSchemaType, jsonEncoder: JsonEncoder<*>): Field =
        Field(
            "id",
            object : FieldType {
                override val airbyteSchemaType = airbyteSchemaType
                override val jsonEncoder = jsonEncoder
            }
        )

    val testCases =
        listOf(
            TestCase(
                value = 123L,
                jsonEncoder = LongCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.INTEGER,
            ),
            TestCase(
                value = 123,
                jsonEncoder = IntCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.INTEGER
            ),
            TestCase(
                value = "text value",
                jsonEncoder = TextCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.STRING
            ),
            TestCase(
                value = true,
                jsonEncoder = BooleanCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.BOOLEAN
            ),
            TestCase(
                value =
                    OffsetDateTime.parse(
                        OffsetDateTime.now().format(OffsetDateTimeCodec.formatter)
                    ),
                jsonEncoder = OffsetDateTimeCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE
            ),
            TestCase(
                value = 123.456f,
                jsonEncoder = FloatCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.NUMBER
            ),
            TestCase(
                value = ByteBuffer.wrap("hello".toByteArray()),
                jsonEncoder = BinaryCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.BINARY
            ),
            TestCase(
                value = BigDecimal.valueOf(1234.567),
                jsonEncoder = BigDecimalCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.NUMBER
            ),
            TestCase(
                value = BigDecimal.valueOf(987),
                jsonEncoder = BigDecimalIntegerCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.INTEGER
            ),
            TestCase(
                value = 12.toShort(),
                jsonEncoder = ShortCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.INTEGER
            ),
            TestCase(
                value = 123.toByte(),
                jsonEncoder = ByteCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.INTEGER
            ),
            TestCase(
                value = 12345.678,
                jsonEncoder = DoubleCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.NUMBER
            ),
            TestCase(
                value = ByteBuffer.wrap("{\"hello\":1234}".toByteArray()),
                jsonEncoder = JsonBytesCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.JSONB
            ),
            TestCase(
                value = "{\"hello\":1234}",
                jsonEncoder = JsonStringCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.JSONB
            ),
            TestCase(
                value = URI("http://www.example.com").toURL(),
                jsonEncoder = UrlCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.STRING
            ),
            TestCase(
                value = LocalDate.now(),
                jsonEncoder = LocalDateCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.DATE
            ),
            TestCase(
                value = LocalTime.parse(LocalTime.now().format(LocalTimeCodec.formatter)),
                jsonEncoder = LocalTimeCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE
            ),
            TestCase(
                value =
                    LocalDateTime.parse(LocalDateTime.now().format(LocalDateTimeCodec.formatter)),
                jsonEncoder = LocalDateTimeCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE
            ),
            TestCase(
                value = OffsetTime.parse(OffsetTime.now().format(OffsetTimeCodec.formatter)),
                jsonEncoder = OffsetTimeCodec,
                airbyteSchemaType = LeafAirbyteSchemaType.TIME_WITH_TIMEZONE
            ),
        )

    @TestFactory
    fun dynamicTestsForAddition(): Collection<DynamicNode> {

        return testCases.map { case ->
            @Suppress("UNCHECKED_CAST")
            val fve = FieldValueEncoder(case.value, case.jsonEncoder as JsonEncoder<in Any>)
            DynamicTest.dynamicTest("test-${case.value!!.javaClass.simpleName}") {
                val n: NativeRecordPayload = mutableMapOf("id" to fve)
                val field = fieldOf(case.airbyteSchemaType, case.jsonEncoder)
                val actualProto = n.toProtobuf(setOf(field), protoBuilder, valBuilder).build()
                assertEquals(case.asDecoderType, protoDecoder.decode(actualProto.getData(0)))
            }
        }
    }
}
