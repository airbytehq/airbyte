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
import java.nio.ByteBuffer
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime

/**
 * Root of our own type hierarchy for Airbyte record fields.
 */
interface FieldType : JdbcGetter<JsonNode> {
    val airbyteType: AirbyteType
}

interface ReversibleFieldType : FieldType, JdbcSetter<JsonNode>

abstract class FieldTypeBase<R>(
    override val airbyteType: AirbyteType,
    val jdbcGetter: JdbcGetter<out R>,
    val jsonEncoder: JsonEncoder<R>,
) : FieldType {

    override fun get(rs: ResultSet, colIdx: Int): JsonNode =
        when (val decoded: R? = jdbcGetter.get(rs, colIdx)) {
            null -> NullCodec.encode(null)
            else -> jsonEncoder.encode(decoded)
        }
}

abstract class ReversibleFieldTypeBase<R, W>(
    airbyteType: AirbyteType,
    jdbcGetter: JdbcGetter<out R>,
    jsonEncoder: JsonEncoder<R>,
    val jsonDecoder: JsonDecoder<W>,
    val jdbcSetter: JdbcSetter<in W>,
) : FieldTypeBase<R>(airbyteType, jdbcGetter, jsonEncoder), ReversibleFieldType {

    override fun set(stmt: PreparedStatement, paramIdx: Int, value: JsonNode) {
        jdbcSetter.set(stmt, paramIdx, jsonDecoder.decode(value))
    }
}

abstract class SymmetricFieldTypeBase<T>(
    airbyteType: AirbyteType,
    jdbcAccessor: JdbcAccessor<T>,
    jsonCodec: JsonCodec<T>,
) : ReversibleFieldTypeBase<T,T>(airbyteType, jdbcAccessor, jsonCodec, jsonCodec, jdbcAccessor)

data object BooleanFieldType : SymmetricFieldTypeBase<Boolean>(
    LeafAirbyteType.BOOLEAN,
    BooleanAccessor,
    BooleanCodec,
)

data object BigDecimalFieldType : SymmetricFieldTypeBase<BigDecimal>(
    LeafAirbyteType.NUMBER,
    BigDecimalAccessor,
    BigDecimalCodec,
)

data object DoubleFieldType : SymmetricFieldTypeBase<Double>(
    LeafAirbyteType.NUMBER,
    DoubleAccessor,
    DoubleCodec,
)

data object FloatFieldType : SymmetricFieldTypeBase<Float>(
    LeafAirbyteType.NUMBER,
    FloatAccessor,
    FloatCodec,
)

data object BigIntegerFieldType : SymmetricFieldTypeBase<BigDecimal>(
    LeafAirbyteType.INTEGER,
    BigDecimalAccessor,
    BigDecimalIntegerCodec,
)

data object LongFieldType : SymmetricFieldTypeBase<Long>(
    LeafAirbyteType.INTEGER,
    LongAccessor,
    LongCodec,
)

data object IntFieldType : SymmetricFieldTypeBase<Int>(
    LeafAirbyteType.INTEGER,
    IntAccessor,
    IntCodec,
)

data object ShortFieldType : SymmetricFieldTypeBase<Short>(
    LeafAirbyteType.INTEGER,
    ShortAccessor,
    ShortCodec,
)

data object ByteFieldType : SymmetricFieldTypeBase<Byte>(
    LeafAirbyteType.INTEGER,
    ByteAccessor,
    ByteCodec,
)

data object StringFieldType : SymmetricFieldTypeBase<String>(
    LeafAirbyteType.STRING,
    StringAccessor,
    TextCodec,
)

data object NStringFieldType : SymmetricFieldTypeBase<String>(
    LeafAirbyteType.STRING,
    NStringAccessor,
    TextCodec,
)

data object CharacterStreamFieldType : SymmetricFieldTypeBase<String>(
    LeafAirbyteType.STRING,
    CharacterStreamAccessor,
    TextCodec,
)

data object NCharacterStreamFieldType : SymmetricFieldTypeBase<String>(
    LeafAirbyteType.STRING,
    NCharacterStreamAccessor,
    TextCodec,
)

data object ClobFieldType : SymmetricFieldTypeBase<String>(
    LeafAirbyteType.STRING,
    ClobAccessor,
    TextCodec,
)

data object NClobFieldType : SymmetricFieldTypeBase<String>(
    LeafAirbyteType.STRING,
    NClobAccessor,
    TextCodec,
)

data object XmlFieldType : SymmetricFieldTypeBase<String>(
    LeafAirbyteType.STRING,
    XmlAccessor,
    TextCodec,
)

data object UrlFieldType : SymmetricFieldTypeBase<URL>(
    LeafAirbyteType.STRING,
    UrlAccessor,
    UrlCodec,
)

data object BytesFieldType : SymmetricFieldTypeBase<ByteBuffer>(
    LeafAirbyteType.BINARY,
    BytesAccessor,
    BinaryCodec,
)

data object BinaryStreamFieldType : SymmetricFieldTypeBase<ByteBuffer>(
    LeafAirbyteType.BINARY,
    BinaryStreamAccessor,
    BinaryCodec,
)

data object JsonStringFieldType : SymmetricFieldTypeBase<String>(
    LeafAirbyteType.JSONB,
    StringAccessor,
    JsonStringCodec
)

data object LocalDateFieldType : SymmetricFieldTypeBase<LocalDate>(
    LeafAirbyteType.DATE,
    DateAccessor,
    LocalDateCodec,
)

data object LocalTimeFieldType : SymmetricFieldTypeBase<LocalTime>(
    LeafAirbyteType.TIME_WITHOUT_TIMEZONE,
    TimeAccessor,
    LocalTimeCodec,
)

data object LocalDateTimeFieldType : SymmetricFieldTypeBase<LocalDateTime>(
    LeafAirbyteType.TIMESTAMP_WITHOUT_TIMEZONE,
    TimestampAccessor,
    LocalDateTimeCodec,
)

data object OffsetTimeFieldType : ReversibleFieldTypeBase<OffsetTime, OffsetTime>(
    LeafAirbyteType.TIME_WITH_TIMEZONE,
    ObjectGetter(OffsetTime::class.java),
    OffsetTimeCodec,
    OffsetTimeCodec,
    AnyAccessor,
)

data object OffsetDateTimeFieldType : ReversibleFieldTypeBase<OffsetDateTime, OffsetDateTime>(
    LeafAirbyteType.TIMESTAMP_WITH_TIMEZONE,
    ObjectGetter(OffsetDateTime::class.java),
    OffsetDateTimeCodec,
    OffsetDateTimeCodec,
    AnyAccessor,
)

data object PokemonFieldType : FieldTypeBase<Any>(
    LeafAirbyteType.STRING,
    StringAccessor,
    AnyEncoder
)

data object NullFieldType : FieldTypeBase<Any?>(
    LeafAirbyteType.NULL,
    AnyAccessor,
    NullCodec
)

data class ArrayFieldType<T>(val elementFieldType: FieldTypeBase<T>) : FieldTypeBase<List<T>>(
    ArrayAirbyteType(elementFieldType.airbyteType),
    ArrayGetter(elementFieldType.jdbcGetter),
    ArrayEncoder(elementFieldType.jsonEncoder),
)
