/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.data

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.net.URI
import java.nio.ByteBuffer
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.time.temporal.ChronoUnit
import java.util.UUID
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JsonCodecTest {
    private fun <T> JsonCodec<T>.testValueRoundTrip(x: T) {
        Assertions.assertEquals(x, decode(encode(x)))
    }

    private fun <T> JsonCodec<T>.testJsonRoundTrip(x: JsonNode) {
        Assertions.assertEquals(x.toString(), encode(decode(x)).toString())
    }

    private fun <T> JsonCodec<T>.testBadEncoding(x: JsonNode) {
        Assertions.assertThrows(IllegalArgumentException::class.java) { decode(x) }
    }

    @Test
    fun testBoolean() {
        BooleanCodec.run {
            testValueRoundTrip(false)
            testValueRoundTrip(true)
            testJsonRoundTrip(Jsons.booleanNode(false))
            testJsonRoundTrip(Jsons.booleanNode(true))
            testBadEncoding(Jsons.textNode("true"))
            testBadEncoding(Jsons.numberNode(1))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testText() {
        TextCodec.run {
            testValueRoundTrip("")
            testValueRoundTrip("foo")
            testJsonRoundTrip(Jsons.textNode(""))
            testJsonRoundTrip(Jsons.textNode("foo"))
            testBadEncoding(Jsons.binaryNode("foo".toByteArray()))
            testBadEncoding(Jsons.numberNode(1))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testBinary() {
        BinaryCodec.run {
            testValueRoundTrip(ByteBuffer.wrap(ByteArray(0)))
            testValueRoundTrip(ByteBuffer.wrap("foo".toByteArray()))
            testJsonRoundTrip(Jsons.binaryNode("".toByteArray()))
            testJsonRoundTrip(Jsons.binaryNode("foo".toByteArray()))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.numberNode(1))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testBigDecimal() {
        BigDecimalCodec.run {
            testValueRoundTrip(BigDecimal.ZERO)
            testValueRoundTrip(BigDecimal.ONE)
            testValueRoundTrip(BigDecimal(Long.MAX_VALUE).multiply(BigDecimal(1.1)))
            testJsonRoundTrip(Jsons.numberNode(0))
            testJsonRoundTrip(Jsons.numberNode(1))
            testJsonRoundTrip(Jsons.numberNode(-123.456))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testBigDecimalInteger() {
        BigDecimalIntegerCodec.run {
            testValueRoundTrip(BigDecimal.ZERO)
            testValueRoundTrip(BigDecimal.ONE)
            testValueRoundTrip(BigDecimal(Long.MAX_VALUE).multiply(BigDecimal(2)))
            testJsonRoundTrip(Jsons.numberNode(0))
            testJsonRoundTrip(Jsons.numberNode(1))
            testBadEncoding(Jsons.numberNode(BigDecimal(Long.MAX_VALUE).multiply(BigDecimal(1.1))))
            testBadEncoding(Jsons.numberNode(123.456))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testLong() {
        LongCodec.run {
            testValueRoundTrip(0L)
            testValueRoundTrip(1L)
            testValueRoundTrip(Long.MAX_VALUE)
            testJsonRoundTrip(Jsons.numberNode(0))
            testJsonRoundTrip(Jsons.numberNode(1))
            testBadEncoding(Jsons.numberNode(BigDecimal(Long.MAX_VALUE).multiply(BigDecimal(2))))
            testBadEncoding(Jsons.numberNode(123.456))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testInt() {
        IntCodec.run {
            testValueRoundTrip(0)
            testValueRoundTrip(1)
            testJsonRoundTrip(Jsons.numberNode(0))
            testJsonRoundTrip(Jsons.numberNode(1))
            testBadEncoding(Jsons.numberNode(Long.MAX_VALUE))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testShort() {
        ShortCodec.run {
            testValueRoundTrip(0)
            testValueRoundTrip(1)
            testJsonRoundTrip(Jsons.numberNode(0))
            testJsonRoundTrip(Jsons.numberNode(1))
            testBadEncoding(Jsons.numberNode(Int.MAX_VALUE))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testByte() {
        ByteCodec.run {
            testValueRoundTrip(0)
            testValueRoundTrip(1)
            testJsonRoundTrip(Jsons.numberNode(0))
            testJsonRoundTrip(Jsons.numberNode(1))
            testBadEncoding(Jsons.numberNode(Short.MAX_VALUE))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testDouble() {
        DoubleCodec.run {
            testValueRoundTrip(0.0)
            testValueRoundTrip(0.1)
            testJsonRoundTrip(Jsons.numberNode(0.0))
            testJsonRoundTrip(Jsons.numberNode(1.0))
            testJsonRoundTrip(Jsons.numberNode(-123.456))
            testJsonRoundTrip(Jsons.numberNode(0.000000000000000000000000000000000001))
            testBadEncoding(Jsons.numberNode(BigDecimal(Long.MAX_VALUE / 3.0).pow(2)))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testFloat() {
        FloatCodec.run {
            testValueRoundTrip(0.0f)
            testValueRoundTrip(0.1f)
            testJsonRoundTrip(Jsons.numberNode(0.0f))
            testJsonRoundTrip(Jsons.numberNode(1.0f))
            testJsonRoundTrip(Jsons.numberNode(-123.456f))
            testBadEncoding(Jsons.numberNode(0.000000000000000000000000000000000001))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testJsonBytes() {
        JsonBytesCodec.run {
            testValueRoundTrip(ByteBuffer.wrap("{}".toByteArray()))
            testValueRoundTrip(ByteBuffer.wrap("[123]".toByteArray()))
            testJsonRoundTrip(Jsons.objectNode())
            testJsonRoundTrip(Jsons.arrayNode())
            testBadEncoding(Jsons.textNode("{}"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testJsonString() {
        JsonStringCodec.run {
            testValueRoundTrip("{}")
            testValueRoundTrip("[123]")
            testJsonRoundTrip(Jsons.objectNode())
            testJsonRoundTrip(Jsons.arrayNode())
            testBadEncoding(Jsons.textNode("{}"))
            testBadEncoding(Jsons.textNode("123"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testUrl() {
        UrlCodec.run {
            testValueRoundTrip(URI.create("http://localhost/").toURL())
            testJsonRoundTrip(Jsons.textNode("http://localhost/"))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testLocalDate() {
        LocalDateCodec.run {
            testValueRoundTrip(LocalDate.now())
            testJsonRoundTrip(Jsons.textNode("2024-03-01"))
            testBadEncoding(Jsons.textNode("01-AUG-2024"))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testLocalTime() {
        LocalTimeCodec.run {
            testValueRoundTrip(LocalTime.now().truncatedTo(ChronoUnit.MICROS))
            testJsonRoundTrip(Jsons.textNode("01:02:03.456789"))
            testBadEncoding(Jsons.textNode("01:02:03.4"))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testLocalDateTime() {
        LocalDateTimeCodec.run {
            testValueRoundTrip(LocalDateTime.now().truncatedTo(ChronoUnit.MICROS))
            testJsonRoundTrip(Jsons.textNode("2024-03-01T01:02:03.456789"))
            testBadEncoding(Jsons.textNode("2024-03-01 01:02:03.4"))
            testBadEncoding(Jsons.numberNode(LocalDateTime.now().toEpochSecond(ZoneOffset.UTC)))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testOffsetTime() {
        OffsetTimeCodec.run {
            testValueRoundTrip(OffsetTime.now().truncatedTo(ChronoUnit.MICROS))
            testJsonRoundTrip(Jsons.textNode("01:02:03.456789-04:30"))
            testBadEncoding(Jsons.textNode("01:02:03.456789"))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testOffsetDateTime() {
        OffsetDateTimeCodec.run {
            testValueRoundTrip(OffsetDateTime.now().truncatedTo(ChronoUnit.MICROS))
            testJsonRoundTrip(Jsons.textNode("2024-03-01T01:02:03.456789-04:30"))
            testBadEncoding(Jsons.textNode("2024-03-01T01:02:03.456789"))
            testBadEncoding(Jsons.numberNode(OffsetDateTime.now().toEpochSecond()))
            testBadEncoding(Jsons.textNode("foo"))
            testBadEncoding(Jsons.nullNode())
        }
    }

    @Test
    fun testNull() {
        NullCodec.run {
            testValueRoundTrip(null)
            testJsonRoundTrip(Jsons.nullNode())
            Assertions.assertEquals(null, decode(encode("foo")))
        }
    }

    @Test
    fun testAnyEncoder() {
        val uuid: UUID = UUID.randomUUID()
        AnyEncoder.run {
            Assertions.assertEquals(Jsons.textNode("foo"), encode("foo"))
            Assertions.assertEquals(Jsons.textNode("123"), encode(BigDecimal(123)))
            Assertions.assertEquals(Jsons.textNode(uuid.toString()), encode(uuid))
        }
    }

    @Test
    fun testArrayEncoder() {
        ArrayEncoder(IntCodec).run {
            Assertions.assertEquals(
                Jsons.arrayNode().add(1).add(2).add(3),
                encode(listOf(1, 2, 3)),
            )
        }
        ArrayEncoder(ArrayEncoder(IntCodec)).run {
            Assertions.assertEquals(
                Jsons.arrayNode()
                    .add(Jsons.arrayNode().add(1).add(2))
                    .add(Jsons.arrayNode().add(3)),
                encode(listOf(listOf(1, 2), listOf(3))),
            )
        }
    }

    @Test
    fun testArrayDecoder() {
        ArrayDecoder(IntCodec).run {
            Assertions.assertEquals(
                listOf(1, 2, 3),
                decode(
                    Jsons.arrayNode().add(1).add(2).add(3),
                ),
            )
        }
        ArrayDecoder(ArrayDecoder(IntCodec)).run {
            Assertions.assertEquals(
                listOf(listOf(1, 2), listOf(3)),
                decode(
                    Jsons.arrayNode()
                        .add(Jsons.arrayNode().add(1).add(2))
                        .add(Jsons.arrayNode().add(3)),
                ),
            )
            Assertions.assertThrows(IllegalArgumentException::class.java) {
                decode(Jsons.objectNode())
            }
            Assertions.assertThrows(IllegalArgumentException::class.java) {
                decode(Jsons.textNode("[]"))
            }
            Assertions.assertThrows(IllegalArgumentException::class.java) {
                decode(Jsons.nullNode())
            }
        }
    }
}
