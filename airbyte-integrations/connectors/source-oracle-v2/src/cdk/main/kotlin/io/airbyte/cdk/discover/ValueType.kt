/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.discover

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.jdbc.AnyAccessor
import io.airbyte.cdk.jdbc.ArrayGetter
import io.airbyte.cdk.jdbc.BigDecimalAccessor
import io.airbyte.cdk.jdbc.BinaryStreamAccessor
import io.airbyte.cdk.jdbc.BooleanAccessor
import io.airbyte.cdk.jdbc.ByteAccessor
import io.airbyte.cdk.jdbc.BytesAccessor
import io.airbyte.cdk.jdbc.CharacterStreamAccessor
import io.airbyte.cdk.jdbc.ClobAccessor
import io.airbyte.cdk.jdbc.DateAccessor
import io.airbyte.cdk.jdbc.DoubleAccessor
import io.airbyte.cdk.jdbc.FloatAccessor
import io.airbyte.cdk.jdbc.IntAccessor
import io.airbyte.cdk.jdbc.JdbcAccessor
import io.airbyte.cdk.jdbc.JdbcGetter
import io.airbyte.cdk.jdbc.JdbcSetter
import io.airbyte.cdk.jdbc.LongAccessor
import io.airbyte.cdk.jdbc.NCharacterStreamAccessor
import io.airbyte.cdk.jdbc.NClobAccessor
import io.airbyte.cdk.jdbc.NStringAccessor
import io.airbyte.cdk.jdbc.ObjectGetter
import io.airbyte.cdk.jdbc.ShortAccessor
import io.airbyte.cdk.jdbc.StringAccessor
import io.airbyte.cdk.jdbc.TimeAccessor
import io.airbyte.cdk.jdbc.TimestampAccessor
import io.airbyte.cdk.jdbc.UrlAccessor
import io.airbyte.cdk.jdbc.XmlAccessor
import io.airbyte.cdk.read.AnyEncoder
import io.airbyte.cdk.read.ArrayEncoder
import io.airbyte.cdk.read.BigDecimalCodec
import io.airbyte.cdk.read.BigDecimalIntegerCodec
import io.airbyte.cdk.read.BinaryCodec
import io.airbyte.cdk.read.BooleanCodec
import io.airbyte.cdk.read.ByteCodec
import io.airbyte.cdk.read.DoubleCodec
import io.airbyte.cdk.read.FloatCodec
import io.airbyte.cdk.read.IntCodec
import io.airbyte.cdk.read.JsonCodec
import io.airbyte.cdk.read.JsonDecoder
import io.airbyte.cdk.read.JsonEncoder
import io.airbyte.cdk.read.JsonStringCodec
import io.airbyte.cdk.read.LocalDateCodec
import io.airbyte.cdk.read.LocalDateTimeCodec
import io.airbyte.cdk.read.LocalTimeCodec
import io.airbyte.cdk.read.LongCodec
import io.airbyte.cdk.read.NullCodec
import io.airbyte.cdk.read.OffsetDateTimeCodec
import io.airbyte.cdk.read.OffsetTimeCodec
import io.airbyte.cdk.read.ShortCodec
import io.airbyte.cdk.read.TextCodec
import io.airbyte.cdk.read.UrlCodec
import java.math.BigDecimal
import java.net.URL
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime

interface ValueType<R> : JdbcGetter<JsonNode> {

    val jdbcGetter: JdbcGetter<out R>
    val jsonEncoder: JsonEncoder<R>
    val airbyteType: AirbyteType

    override fun get(rs: ResultSet, colIdx: Int): JsonNode =
        when (val decoded: R? = jdbcGetter.get(rs, colIdx)) {
            null -> NullCodec.encode(null)
            else -> jsonEncoder.encode(decoded)
        }
}

interface ReversibleValueType<R, W> : ValueType<R>, JdbcSetter<JsonNode> {

    val jsonDecoder: JsonDecoder<W>
    val jdbcSetter: JdbcSetter<in W>

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: JsonNode) {
        jdbcSetter.set(stmt, paramIdx, jsonDecoder.decode(value))
    }
}

interface SymmetricValueType<T> : ReversibleValueType<T, T> {

    val jdbcAccessor: JdbcAccessor<T>
    val jsonCodec: JsonCodec<T>

    override val jdbcGetter: JdbcGetter<T>
        get() = jdbcAccessor
    override val jsonEncoder: JsonEncoder<T>
        get() = jsonCodec
    override val jsonDecoder: JsonDecoder<T>
        get() = jsonCodec
    override val jdbcSetter: JdbcSetter<T>
        get() = jdbcAccessor
}

data object BooleanValueType : SymmetricValueType<Boolean> {

    override val jdbcAccessor: JdbcAccessor<Boolean>
        get() = BooleanAccessor
    override val jsonCodec: JsonCodec<Boolean>
        get() = BooleanCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.BOOLEAN
}

data object BigDecimalValueType : SymmetricValueType<BigDecimal> {

    override val jdbcAccessor: JdbcAccessor<BigDecimal>
        get() = BigDecimalAccessor
    override val jsonCodec: JsonCodec<BigDecimal>
        get() = BigDecimalCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.NUMBER
}

data object DoubleValueType : SymmetricValueType<Double> {

    override val jdbcAccessor: JdbcAccessor<Double>
        get() = DoubleAccessor
    override val jsonCodec: JsonCodec<Double>
        get() = DoubleCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.NUMBER
}

data object FloatValueType : SymmetricValueType<Float> {

    override val jdbcAccessor: JdbcAccessor<Float>
        get() = FloatAccessor
    override val jsonCodec: JsonCodec<Float>
        get() = FloatCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.NUMBER
}

data object BigIntegerValueType : SymmetricValueType<BigDecimal> {

    override val jdbcAccessor: JdbcAccessor<BigDecimal>
        get() = BigDecimalAccessor
    override val jsonCodec: JsonCodec<BigDecimal>
        get() = BigDecimalIntegerCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.INTEGER
}

data object LongValueType : SymmetricValueType<Long> {

    override val jdbcAccessor: JdbcAccessor<Long>
        get() = LongAccessor
    override val jsonCodec: JsonCodec<Long>
        get() = LongCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.INTEGER
}

data object IntValueType : SymmetricValueType<Int> {

    override val jdbcAccessor: JdbcAccessor<Int>
        get() = IntAccessor
    override val jsonCodec: JsonCodec<Int>
        get() = IntCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.INTEGER
}

data object ShortValueType : SymmetricValueType<Short> {

    override val jdbcAccessor: JdbcAccessor<Short>
        get() = ShortAccessor
    override val jsonCodec: JsonCodec<Short>
        get() = ShortCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.INTEGER
}

data object ByteValueType : SymmetricValueType<Byte> {

    override val jdbcAccessor: JdbcAccessor<Byte>
        get() = ByteAccessor
    override val jsonCodec: JsonCodec<Byte>
        get() = ByteCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.INTEGER
}

data object StringValueType : SymmetricValueType<String> {

    override val jdbcAccessor: JdbcAccessor<String>
        get() = StringAccessor
    override val jsonCodec: JsonCodec<String>
        get() = TextCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object NStringValueType : SymmetricValueType<String> {

    override val jdbcAccessor: JdbcAccessor<String>
        get() = NStringAccessor
    override val jsonCodec: JsonCodec<String>
        get() = TextCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object CharacterStreamValueType : SymmetricValueType<String> {

    override val jdbcAccessor: JdbcAccessor<String>
        get() = CharacterStreamAccessor
    override val jsonCodec: JsonCodec<String>
        get() = TextCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object NCharacterStreamValueType : SymmetricValueType<String> {

    override val jdbcAccessor: JdbcAccessor<String>
        get() = NCharacterStreamAccessor
    override val jsonCodec: JsonCodec<String>
        get() = TextCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object ClobValueType : SymmetricValueType<String> {

    override val jdbcAccessor: JdbcAccessor<String>
        get() = ClobAccessor
    override val jsonCodec: JsonCodec<String>
        get() = TextCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object NClobValueType : SymmetricValueType<String> {

    override val jdbcAccessor: JdbcAccessor<String>
        get() = NClobAccessor
    override val jsonCodec: JsonCodec<String>
        get() = TextCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object XmlValueType : SymmetricValueType<String> {

    override val jdbcAccessor: JdbcAccessor<String>
        get() = XmlAccessor
    override val jsonCodec: JsonCodec<String>
        get() = TextCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object UrlValueType : SymmetricValueType<URL> {

    override val jdbcAccessor: JdbcAccessor<URL>
        get() = UrlAccessor
    override val jsonCodec: JsonCodec<URL>
        get() = UrlCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object BytesValueType : SymmetricValueType<ByteArray> {

    override val jdbcAccessor: JdbcAccessor<ByteArray>
        get() = BytesAccessor
    override val jsonCodec: JsonCodec<ByteArray>
        get() = BinaryCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.BINARY
}

data object BinaryStreamValueType : SymmetricValueType<ByteArray> {

    override val jdbcAccessor: JdbcAccessor<ByteArray>
        get() = BinaryStreamAccessor
    override val jsonCodec: JsonCodec<ByteArray>
        get() = BinaryCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.BINARY
}

data object LocalDateValueType : SymmetricValueType<LocalDate> {

    override val jdbcAccessor: JdbcAccessor<LocalDate>
        get() = DateAccessor
    override val jsonCodec: JsonCodec<LocalDate>
        get() = LocalDateCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.DATE
}

data object LocalTimeValueType : SymmetricValueType<LocalTime> {

    override val jdbcAccessor: JdbcAccessor<LocalTime>
        get() = TimeAccessor
    override val jsonCodec: JsonCodec<LocalTime>
        get() = LocalTimeCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.TIME_WITHOUT_TIMEZONE
}

data object LocalDateTimeValueType : SymmetricValueType<LocalDateTime> {

    override val jdbcAccessor: JdbcAccessor<LocalDateTime>
        get() = TimestampAccessor
    override val jsonCodec: JsonCodec<LocalDateTime>
        get() = LocalDateTimeCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.TIMESTAMP_WITHOUT_TIMEZONE
}

data object OffsetTimeValueType : ReversibleValueType<OffsetTime, OffsetTime> {

    override val jdbcGetter: JdbcGetter<out OffsetTime>
        get() = ObjectGetter(OffsetTime::class.java)
    override val jsonEncoder: JsonEncoder<OffsetTime>
        get() = OffsetTimeCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.TIME_WITH_TIMEZONE
    override val jsonDecoder: JsonDecoder<OffsetTime>
        get() = OffsetTimeCodec
    override val jdbcSetter: JdbcSetter<in OffsetTime>
        get() = AnyAccessor
}

data object OffsetDateTimeValueType : ReversibleValueType<OffsetDateTime, OffsetDateTime> {

    override val jdbcGetter: JdbcGetter<out OffsetDateTime>
        get() = ObjectGetter(OffsetDateTime::class.java)
    override val jsonEncoder: JsonEncoder<OffsetDateTime>
        get() = OffsetDateTimeCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE
    override val jsonDecoder: JsonDecoder<OffsetDateTime>
        get() = OffsetDateTimeCodec
    override val jdbcSetter: JdbcSetter<in OffsetDateTime>
        get() = AnyAccessor
}

data object OneWayAnyValueType : ValueType<Any> {

    override val jdbcGetter: JdbcGetter<out Any>
        get() = AnyAccessor
    override val jsonEncoder: JsonEncoder<Any>
        get() = AnyEncoder
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object OneWayStringValueType : ValueType<Any> {

    override val jdbcGetter: JdbcGetter<out Any>
        get() = StringAccessor
    override val jsonEncoder: JsonEncoder<Any>
        get() = AnyEncoder
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.STRING
}

data object OneWayNullValueType : ValueType<Any?> {

    override val jdbcGetter: JdbcGetter<out Any?>
        get() = AnyAccessor
    override val jsonEncoder: JsonEncoder<Any?>
        get() = NullCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.NULL
}

data object JsonStringValueType : SymmetricValueType<String> {

    override val jdbcAccessor: JdbcAccessor<String>
        get() = StringAccessor
    override val jsonCodec: JsonCodec<String>
        get() = JsonStringCodec
    override val airbyteType: AirbyteType
        get() = LeafAirbyteType.JSONB
}

data class ArrayValueType<T>(val elementValueType: ValueType<T>) : ValueType<List<T>> {

    override val jdbcGetter: JdbcGetter<out List<T>>
        get() = ArrayGetter(elementValueType.jdbcGetter)
    override val jsonEncoder: JsonEncoder<List<T>>
        get() = ArrayEncoder(elementValueType.jsonEncoder)
    override val airbyteType: AirbyteType
        get() = ArrayAirbyteType(elementValueType.airbyteType)
}
