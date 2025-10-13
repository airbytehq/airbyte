/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output.sockets

import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BinaryCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.ByteCodec
import io.airbyte.cdk.data.CdcOffsetDateTimeCodec
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
import io.airbyte.cdk.data.OffsetDateTimeCodec
import io.airbyte.cdk.data.OffsetTimeCodec
import io.airbyte.cdk.data.ShortCodec
import io.airbyte.cdk.data.TextCodec
import io.airbyte.cdk.data.UrlCodec
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.discover.StringFieldType
import io.airbyte.cdk.protocol.AirbyteValueProtobufDecoder
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteRecordMessageProtobuf
import io.airbyte.protocol.protobuf.AirbyteRecordMessage.AirbyteValueProtobuf
import java.math.BigDecimal
import java.math.BigInteger
import java.net.URI
import java.nio.ByteBuffer
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.util.Base64
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.DynamicNode
import org.junit.jupiter.api.DynamicTest
import org.junit.jupiter.api.TestFactory

class NativeRecordProtobufEncoderTest {
    private val protoDecoder = AirbyteValueProtobufDecoder()

    data class TestCase<T>(
        val value: T,
        val jsonEncoder: JsonEncoder<*>,
        val decoder: (AirbyteRecordMessageProtobuf) -> T
    )

    val valBuilder = AirbyteValueProtobuf.newBuilder()
    val protoBuilder =
        AirbyteRecordMessageProtobuf.newBuilder().also { it.addData(0, valBuilder.clear()) }

    val testCases =
        listOf(
            TestCase(
                value = 123L,
                jsonEncoder = LongCodec,
                decoder = { proto ->
                    (protoDecoder.decode(proto.getData(0)) as BigInteger).toLong()
                }
            ),
            TestCase(
                value = 123,
                jsonEncoder = IntCodec,
                decoder = { proto -> (protoDecoder.decode(proto.getData(0)) as BigInteger).toInt() }
            ),
            TestCase(
                value = "text value",
                jsonEncoder = TextCodec,
                decoder = { proto -> protoDecoder.decode(proto.getData(0)) }
            ),
            TestCase(
                value = true,
                jsonEncoder = BooleanCodec,
                decoder = { proto -> protoDecoder.decode(proto.getData(0)) }
            ),
            TestCase(
                value =
                    OffsetDateTime.parse(
                        OffsetDateTime.now().format(OffsetDateTimeCodec.formatter)
                    ),
                jsonEncoder = OffsetDateTimeCodec,
                decoder = { proto -> protoDecoder.decode(proto.getData(0)) },
            ),
            TestCase(
                value =
                    OffsetDateTime.parse(
                        OffsetDateTime.now().format(OffsetDateTimeCodec.formatter)
                    ),
                jsonEncoder = CdcOffsetDateTimeCodec,
                decoder = { proto -> OffsetDateTime.parse(proto.getData(0).string) }
            ),
            TestCase(
                value = 123.456f,
                jsonEncoder = FloatCodec,
                decoder = { proto ->
                    (protoDecoder.decode(proto.getData(0)) as BigDecimal).toFloat()
                }
            ),
            TestCase(
                value = "hello".toByteArray().let { ByteBuffer.wrap(it) },
                jsonEncoder = BinaryCodec,
                decoder = { proto ->
                    ByteBuffer.wrap(
                        Base64.getDecoder().decode(protoDecoder.decode(proto.getData(0)) as String)
                    )
                }
            ),
            TestCase(
                value = BigDecimal.valueOf(1234.567),
                jsonEncoder = BigDecimalCodec,
                decoder = { proto -> protoDecoder.decode(proto.getData(0)) }
            ),
            TestCase(
                value = BigDecimal.valueOf(987),
                jsonEncoder = BigDecimalCodec,
                decoder = { proto ->
                    (protoDecoder.decode(proto.getData(0)) as BigInteger).toBigDecimal()
                }
            ),
            TestCase(
                value = 12,
                jsonEncoder = ShortCodec,
                decoder = { proto -> proto.getData(0).integer.toShort() }
            ),
            TestCase(
                value = 123.toByte(),
                jsonEncoder = ByteCodec,
                decoder = { proto -> proto.getData(0).integer.toByte() }
            ),
            TestCase(
                value = 12345.678,
                jsonEncoder = DoubleCodec,
                decoder = { proto -> proto.getData(0).number }
            ),
            TestCase(
                value = "{\"hello\":1234}".toByteArray().let { ByteBuffer.wrap(it) },
                jsonEncoder = JsonBytesCodec,
                decoder = { proto ->
                    ByteBuffer.wrap(
                        Base64.getDecoder().decode(protoDecoder.decode(proto.getData(0)) as String)
                    )
                }
            ),
            TestCase(
                value = "{\"hello\":1234}",
                jsonEncoder = JsonStringCodec,
                decoder = { proto -> proto.getData(0).string }
            ),
            TestCase(
                value = URI("http://www.example.com").toURL(),
                jsonEncoder = UrlCodec,
                decoder = { proto -> URI(protoDecoder.decode(proto.getData(0)) as String).toURL() }
            ),
            TestCase(
                value = LocalDate.now(),
                jsonEncoder = LocalDateCodec,
                decoder = { proto -> protoDecoder.decode(proto.getData(0)) }
            ),
            TestCase(
                value = LocalTime.parse(LocalTime.now().format(LocalTimeCodec.formatter)),
                jsonEncoder = LocalTimeCodec,
                decoder = { proto -> protoDecoder.decode(proto.getData(0)) }
            ),
            TestCase(
                value =
                    LocalDateTime.parse(LocalDateTime.now().format(LocalDateTimeCodec.formatter)),
                jsonEncoder = LocalDateTimeCodec,
                decoder = { proto -> protoDecoder.decode(proto.getData(0)) }
            ),
            TestCase(
                value = OffsetTime.parse(OffsetTime.now().format(OffsetTimeCodec.formatter)),
                jsonEncoder = OffsetTimeCodec,
                decoder = { proto -> protoDecoder.decode(proto.getData(0)) }
            ),
        )
    @TestFactory
    fun dynamicTestsForAddition(): Collection<DynamicNode> {

        return testCases.map { case ->
            @Suppress("UNCHECKED_CAST")
            val fve = FieldValueEncoder(case.value, case.jsonEncoder as JsonEncoder<in Any>)
            DynamicTest.dynamicTest("test-${case.value!!.javaClass.simpleName}") {
                val n: NativeRecordPayload = mutableMapOf("id" to fve)
                val actualProto =
                    n.toProtobuf(setOf(Field("id", StringFieldType)), protoBuilder, valBuilder)
                        .build()
                assertEquals(case.value, case.decoder(actualProto))
            }
        }
    }
}
