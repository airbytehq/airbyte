/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.commons.jackson.MoreMappers
import java.math.BigDecimal
import java.net.URI
import java.net.URL
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeParseException

fun interface JsonEncoder<T> {
    fun encode(decoded: T): JsonNode
}

fun interface JsonDecoder<T> {
    fun decode(encoded: JsonNode): T
}

interface JsonCodec<T> : JsonEncoder<T>, JsonDecoder<T> {
    companion object {
        internal val mapper: ObjectMapper = MoreMappers.initMapper()
        internal val nodeFactory: JsonNodeFactory = mapper.nodeFactory
    }
}

data object NullCodec : JsonCodec<Any?> {

    override fun encode(decoded: Any?): JsonNode = JsonCodec.nodeFactory.nullNode()

    override fun decode(encoded: JsonNode): Any? = null
}

data object AnyEncoder : JsonEncoder<Any> {

    override fun encode(decoded: Any): JsonNode = JsonCodec.nodeFactory.textNode(decoded.toString())
}

data object BooleanCodec : JsonCodec<Boolean> {

    override fun encode(decoded: Boolean): JsonNode = JsonCodec.nodeFactory.booleanNode(decoded)

    override fun decode(encoded: JsonNode): Boolean {
        if (!encoded.isBoolean) {
            throw IllegalArgumentException("invalid boolean value $encoded")
        }
        return encoded.booleanValue()
    }
}

data object TextCodec : JsonCodec<String> {

    override fun encode(decoded: String): JsonNode = JsonCodec.nodeFactory.textNode(decoded)

    override fun decode(encoded: JsonNode): String {
        if (!encoded.isTextual) {
            throw IllegalArgumentException("invalid textual value $encoded")
        }
        return encoded.textValue()
    }
}

data object BinaryCodec : JsonCodec<ByteArray> {

    override fun encode(decoded: ByteArray): JsonNode = JsonCodec.nodeFactory.binaryNode(decoded)

    override fun decode(encoded: JsonNode): ByteArray {
        if (!encoded.isBinary) {
            throw IllegalArgumentException("invalid binary value $encoded")
        }
        return encoded.binaryValue()
    }
}

data object BigDecimalCodec : JsonCodec<BigDecimal> {

    override fun encode(decoded: BigDecimal): JsonNode = JsonCodec.nodeFactory.numberNode(decoded)

    override fun decode(encoded: JsonNode): BigDecimal {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        return encoded.decimalValue()
    }
}

data object BigDecimalIntegerCodec : JsonCodec<BigDecimal> {

    override fun encode(decoded: BigDecimal): JsonNode = JsonCodec.nodeFactory.numberNode(decoded)

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

    override fun encode(decoded: Long): JsonNode = JsonCodec.nodeFactory.numberNode(decoded)

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

    override fun encode(decoded: Int): JsonNode = JsonCodec.nodeFactory.numberNode(decoded)

    override fun decode(encoded: JsonNode): Int = LongCodec.decode(encoded).toInt()
}

data object ShortCodec : JsonCodec<Short> {

    override fun encode(decoded: Short): JsonNode = JsonCodec.nodeFactory.numberNode(decoded)

    override fun decode(encoded: JsonNode): Short = LongCodec.decode(encoded).toShort()
}

data object ByteCodec : JsonCodec<Byte> {

    override fun encode(decoded: Byte): JsonNode = JsonCodec.nodeFactory.numberNode(decoded)

    override fun decode(encoded: JsonNode): Byte = LongCodec.decode(encoded).toByte()
}

data object DoubleCodec : JsonCodec<Double> {

    override fun encode(decoded: Double): JsonNode = JsonCodec.nodeFactory.numberNode(decoded)

    override fun decode(encoded: JsonNode): Double {
        if (!encoded.isNumber) {
            throw IllegalArgumentException("invalid number value $encoded")
        }
        if (!encoded.isFloatingPointNumber) {
            throw IllegalArgumentException("invalid decimal value $encoded")
        }
        if (!encoded.isFloat && !encoded.isDouble) {
            throw IllegalArgumentException("invalid 64-bit floating point value $encoded")
        }
        return encoded.doubleValue()
    }
}

data object FloatCodec : JsonCodec<Float> {

    override fun encode(decoded: Float): JsonNode = JsonCodec.nodeFactory.numberNode(decoded)

    override fun decode(encoded: JsonNode): Float = DoubleCodec.decode(encoded).toFloat()
}

data object JsonBytesCodec : JsonCodec<ByteArray> {

    override fun encode(decoded: ByteArray): JsonNode =
        try {
            JsonCodec.mapper.readTree(decoded)
        } catch (_: Exception) {
            JsonCodec.nodeFactory.textNode(String(decoded))
        }

    override fun decode(encoded: JsonNode): ByteArray {
        if (!encoded.isObject || !encoded.isArray) {
            throw IllegalArgumentException("invalid object or array value $encoded")
        }
        return JsonCodec.mapper.writeValueAsBytes(encoded)
    }
}

data object JsonStringCodec : JsonCodec<String> {

    override fun encode(decoded: String): JsonNode =
        try {
            JsonCodec.mapper.readTree(decoded)
        } catch (_: Exception) {
            JsonCodec.nodeFactory.textNode(decoded)
        }

    override fun decode(encoded: JsonNode): String {
        if (!encoded.isObject || !encoded.isArray) {
            throw IllegalArgumentException("invalid object or array value $encoded")
        }
        return JsonCodec.mapper.writeValueAsString(encoded)
    }
}

data object UrlCodec : JsonCodec<URL> {

    override fun encode(decoded: URL): JsonNode =
        JsonCodec.nodeFactory.textNode(decoded.toExternalForm())

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

    override fun encode(decoded: LocalDate): JsonNode =
        JsonCodec.nodeFactory.textNode(decoded.format(formatter))

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

    override fun encode(decoded: LocalTime): JsonNode =
        JsonCodec.nodeFactory.textNode(decoded.format(formatter))

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
        JsonCodec.nodeFactory.textNode(decoded.format(formatter))

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

    override fun encode(decoded: OffsetTime): JsonNode =
        JsonCodec.nodeFactory.textNode(decoded.format(formatter))

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
        JsonCodec.nodeFactory.textNode(decoded.format(formatter))

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

data class ArrayEncoder<T>(val elementEncoder: JsonEncoder<T>) : JsonEncoder<List<T>> {

    override fun encode(decoded: List<T>): JsonNode =
        JsonCodec.nodeFactory.arrayNode().apply {
            for (e in decoded) {
                add(elementEncoder.encode(e))
            }
        }
}

data class ArrayDecoder<T>(val elementDecoder: JsonDecoder<T>) : JsonDecoder<List<T>> {

    override fun decode(encoded: JsonNode): List<T> {
        if (!encoded.isArray) {
            throw IllegalArgumentException("invalid array value $encoded")
        }
        return encoded.elements().asSequence().map { elementDecoder.decode(it) }.toList()
    }
}
