/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.data

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import java.math.BigDecimal
import java.net.URI
import java.net.URL
import java.nio.ByteBuffer
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException

/** Encodes a field value of type [T] as a [JsonNode] for an Airbyte record or state message. */
fun interface JsonEncoder<T> {
    fun encode(decoded: T): JsonNode
}

/**
 * Decodes a field value of type [T] from a [JsonNode] in an Airbyte state message.
 *
 * Throws an [IllegalArgumentException] when the decoding fails. Implementations of [JsonDecoder]
 * should be strict, failure is unexpected.
 */
fun interface JsonDecoder<T> {
    fun decode(encoded: JsonNode): T
}

/** Combines a [JsonEncoder] and a [JsonDecoder]. */
interface JsonCodec<T> : JsonEncoder<T>, JsonDecoder<T>

data object BooleanCodec : JsonCodec<Boolean> {
    override fun encode(decoded: Boolean): JsonNode = Jsons.booleanNode(decoded)

    override fun decode(encoded: JsonNode): Boolean {
        if (!encoded.isBoolean) {
            throw IllegalArgumentException("invalid boolean value $encoded")
        }
        return encoded.booleanValue()
    }
}

data object TextCodec : JsonCodec<String> {
    override fun encode(decoded: String): JsonNode = Jsons.textNode(decoded)

    override fun decode(encoded: JsonNode): String {
        if (!encoded.isTextual) {
            throw IllegalArgumentException("invalid textual value $encoded")
        }
        return encoded.textValue()
    }
}

data object BinaryCodec : JsonCodec<ByteBuffer> {
    override fun encode(decoded: ByteBuffer): JsonNode = Jsons.binaryNode(decoded)

    override fun decode(encoded: JsonNode): ByteBuffer {
        if (!encoded.isBinary) {
            throw IllegalArgumentException("invalid binary value $encoded")
        }
        return ByteBuffer.wrap(encoded.binaryValue())
    }
}

data object BigDecimalCodec : JsonCodec<BigDecimal> {
    override fun encode(decoded: BigDecimal): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): BigDecimal {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        return encoded.decimalValue()
    }
}

data object BigDecimalIntegerCodec : JsonCodec<BigDecimal> {
    override fun encode(decoded: BigDecimal): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): BigDecimal {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        if (!encoded.canConvertToExactIntegral()) {
            throw IllegalArgumentException("invalid integral value $encoded")
        }
        return encoded.decimalValue()
    }
}

data object LongCodec : JsonCodec<Long> {
    override fun encode(decoded: Long): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): Long {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        if (!encoded.canConvertToExactIntegral()) {
            throw IllegalArgumentException("invalid integral value $encoded")
        }
        if (!encoded.canConvertToLong()) {
            throw IllegalArgumentException("invalid 64-bit integer value $encoded")
        }
        return encoded.longValue()
    }
}

data object IntCodec : JsonCodec<Int> {
    override fun encode(decoded: Int): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): Int {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        if (!encoded.canConvertToExactIntegral()) {
            throw IllegalArgumentException("invalid integral value $encoded")
        }
        if (!encoded.canConvertToInt()) {
            throw IllegalArgumentException("invalid 32-bit integer value $encoded")
        }
        return encoded.intValue()
    }
}

data object ShortCodec : JsonCodec<Short> {
    override fun encode(decoded: Short): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): Short {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        if (!encoded.canConvertToExactIntegral()) {
            throw IllegalArgumentException("invalid integral value $encoded")
        }
        val intValue: Int = encoded.intValue()
        val shortValue: Short = encoded.shortValue()
        if (!encoded.canConvertToInt() || shortValue.toInt() != intValue) {
            throw IllegalArgumentException("invalid 16-bit integer value $encoded")
        }
        return shortValue
    }
}

data object ByteCodec : JsonCodec<Byte> {
    override fun encode(decoded: Byte): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): Byte {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        if (!encoded.canConvertToExactIntegral()) {
            throw IllegalArgumentException("invalid integral value $encoded")
        }
        val intValue: Int = encoded.intValue()
        val byteValue: Byte = intValue.toByte()
        if (!encoded.canConvertToInt() || byteValue.toInt() != intValue) {
            throw IllegalArgumentException("invalid 8-bit integer value $encoded")
        }
        return byteValue
    }
}

data object DoubleCodec : JsonCodec<Double> {
    override fun encode(decoded: Double): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): Double {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        val decoded: Double = encoded.doubleValue()
        if (encode(decoded).decimalValue().compareTo(encoded.decimalValue()) != 0) {
            throw IllegalArgumentException("invalid IEEE-754 64-bit floating point value $encoded")
        }
        return decoded
    }
}

data object FloatCodec : JsonCodec<Float> {
    override fun encode(decoded: Float): JsonNode = Jsons.numberNode(decoded)

    override fun decode(encoded: JsonNode): Float {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        val decoded: Float = encoded.floatValue()
        if (encode(decoded).doubleValue().compareTo(encoded.doubleValue()) != 0) {
            throw IllegalArgumentException("invalid IEEE-754 32-bit floating point value $encoded")
        }
        return decoded
    }
}

data object JsonBytesCodec : JsonCodec<ByteBuffer> {
    override fun encode(decoded: ByteBuffer): JsonNode =
        try {
            Jsons.readTree(decoded.array())
        } catch (_: Exception) {
            Jsons.textNode(String(decoded.array()))
        }

    override fun decode(encoded: JsonNode): ByteBuffer {
        if (!encoded.isObject && !encoded.isArray) {
            throw IllegalArgumentException("invalid object or array value $encoded")
        }
        return ByteBuffer.wrap(Jsons.writeValueAsBytes(encoded))
    }
}

data object JsonStringCodec : JsonCodec<String> {
    override fun encode(decoded: String): JsonNode =
        try {
            Jsons.readTree(decoded)
        } catch (_: Exception) {
            Jsons.textNode(decoded)
        }

    override fun decode(encoded: JsonNode): String {
        if (!encoded.isObject && !encoded.isArray) {
            throw IllegalArgumentException("invalid object or array value $encoded")
        }
        return Jsons.writeValueAsString(encoded)
    }
}

data object UrlCodec : JsonCodec<URL> {
    override fun encode(decoded: URL): JsonNode = Jsons.textNode(decoded.toExternalForm())

    override fun decode(encoded: JsonNode): URL {
        val str: String = TextCodec.decode(encoded)
        try {
            return URI.create(str).toURL()
        } catch (e: Exception) {
            throw IllegalArgumentException("invalid URL value $str", e)
        }
    }
}

data object LocalDateCodec : JsonCodec<LocalDate> {
    override fun encode(decoded: LocalDate): JsonNode = Jsons.textNode(decoded.format(formatter))

    override fun decode(encoded: JsonNode): LocalDate {
        val str: String = TextCodec.decode(encoded)
        try {
            return LocalDate.parse(str, formatter)
        } catch (e: DateTimeParseException) {
            throw IllegalArgumentException("invalid value $str for pattern '$PATTERN'", e)
        }
    }

    const val PATTERN = "yyyy-MM-dd"
    val formatter: DateTimeFormatter = DateTimeFormatter.ofPattern(PATTERN)
}

data object LocalTimeCodec : JsonCodec<LocalTime> {
    override fun encode(decoded: LocalTime): JsonNode = Jsons.textNode(decoded.format(formatter))

    override fun decode(encoded: JsonNode): LocalTime {
        val str: String = TextCodec.decode(encoded)
        try {
            return LocalTime.parse(str, formatter)
        } catch (e: DateTimeParseException) {
            throw IllegalArgumentException("invalid value $str for pattern '$PATTERN'", e)
        }
    }

    const val PATTERN = "HH:mm:ss.SSSSSS"
    val formatter: DateTimeFormatter = DateTimeFormatter.ofPattern(PATTERN)
}

data object LocalDateTimeCodec : JsonCodec<LocalDateTime> {
    override fun encode(decoded: LocalDateTime): JsonNode =
        Jsons.textNode(decoded.format(formatter))

    override fun decode(encoded: JsonNode): LocalDateTime {
        val str: String = TextCodec.decode(encoded)
        try {
            return LocalDateTime.parse(str, formatter)
        } catch (e: DateTimeParseException) {
            throw IllegalArgumentException("invalid value $str for pattern '$PATTERN'", e)
        }
    }

    const val PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSSSSS"
    val formatter: DateTimeFormatter = DateTimeFormatter.ofPattern(PATTERN)
}

data object OffsetTimeCodec : JsonCodec<OffsetTime> {
    override fun encode(decoded: OffsetTime): JsonNode = Jsons.textNode(decoded.format(formatter))

    override fun decode(encoded: JsonNode): OffsetTime {
        val str: String = TextCodec.decode(encoded)
        try {
            return OffsetTime.parse(str, formatter)
        } catch (e: DateTimeParseException) {
            throw IllegalArgumentException("invalid value $str for pattern '$PATTERN'", e)
        }
    }

    const val PATTERN = "HH:mm:ss.SSSSSSXXX"
    val formatter: DateTimeFormatter = DateTimeFormatter.ofPattern(PATTERN)
}

data object OffsetDateTimeCodec : JsonCodec<OffsetDateTime> {
    override fun encode(decoded: OffsetDateTime): JsonNode =
        Jsons.textNode(decoded.format(formatter))

    override fun decode(encoded: JsonNode): OffsetDateTime {
        val str: String = TextCodec.decode(encoded)
        try {
            return OffsetDateTime.parse(str, formatter)
        } catch (e: DateTimeParseException) {
            throw IllegalArgumentException("invalid value $str for pattern '$PATTERN'", e)
        }
    }

    const val PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX"
    val formatter: DateTimeFormatter = DateTimeFormatter.ofPattern(PATTERN)
}

data object NullCodec : JsonCodec<Any?> {
    override fun encode(decoded: Any?): JsonNode = Jsons.nullNode()

    override fun decode(encoded: JsonNode): Any? = null
}

data object AnyEncoder : JsonEncoder<Any> {
    override fun encode(decoded: Any): JsonNode = Jsons.textNode(decoded.toString())
}

data class ArrayEncoder<T>(
    val elementEncoder: JsonEncoder<T>,
) : JsonEncoder<List<T>> {
    override fun encode(decoded: List<T>): JsonNode =
        Jsons.arrayNode().apply {
            for (e in decoded) {
                add(elementEncoder.encode(e))
            }
        }
}

data class ArrayDecoder<T>(
    val elementDecoder: JsonDecoder<T>,
) : JsonDecoder<List<T>> {
    override fun decode(encoded: JsonNode): List<T> {
        if (!encoded.isArray) {
            throw IllegalArgumentException("invalid array value $encoded")
        }
        return encoded.elements().asSequence().map { elementDecoder.decode(it) }.toList()
    }
}
