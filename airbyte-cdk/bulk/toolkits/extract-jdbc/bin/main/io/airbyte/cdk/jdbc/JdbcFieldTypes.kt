/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.data.AirbyteSchemaType
import io.airbyte.cdk.data.AnyEncoder
import io.airbyte.cdk.data.ArrayAirbyteSchemaType
import io.airbyte.cdk.data.ArrayEncoder
import io.airbyte.cdk.data.BigDecimalCodec
import io.airbyte.cdk.data.BigDecimalIntegerCodec
import io.airbyte.cdk.data.BinaryCodec
import io.airbyte.cdk.data.BooleanCodec
import io.airbyte.cdk.data.ByteCodec
import io.airbyte.cdk.data.DoubleCodec
import io.airbyte.cdk.data.FloatCodec
import io.airbyte.cdk.data.IntCodec
import io.airbyte.cdk.data.JsonCodec
import io.airbyte.cdk.data.JsonDecoder
import io.airbyte.cdk.data.JsonEncoder
import io.airbyte.cdk.data.JsonStringCodec
import io.airbyte.cdk.data.LeafAirbyteSchemaType
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
import io.airbyte.cdk.discover.FieldType
import io.airbyte.cdk.discover.LosslessFieldType
import java.lang.reflect.ParameterizedType
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

/** Convenience class for defining concrete [FieldType] objects. */
abstract class JdbcFieldType<R>(
    override val airbyteSchemaType: AirbyteSchemaType,
    val jdbcGetter: JdbcGetter<out R>,
    override val jsonEncoder: JsonEncoder<R>,
) : FieldType, JdbcGetter<JsonNode> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): JsonNode =
        when (val decoded: R? = jdbcGetter.get(rs, colIdx)) {
            null -> NullCodec.encode(null)
            else -> jsonEncoder.encode(decoded)
        }

    @Suppress("UNCHECKED_CAST")
    val genericClass: Class<R> =
        ((javaClass.genericSuperclass as ParameterizedType).actualTypeArguments[0].let {
            if (it is ParameterizedType) it.rawType else it
        })
            as Class<R>
}

/** Convenience class for defining concrete [LosslessFieldType] objects. */
abstract class LosslessJdbcFieldType<R, W>(
    airbyteSchemaType: AirbyteSchemaType,
    jdbcGetter: JdbcGetter<out R>,
    jsonEncoder: JsonEncoder<R>,
    override val jsonDecoder: JsonDecoder<W>,
    val jdbcSetter: JdbcSetter<in W>,
) :
    JdbcFieldType<R>(airbyteSchemaType, jdbcGetter, jsonEncoder),
    LosslessFieldType,
    JdbcSetter<JsonNode> {
    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: JsonNode,
    ) {
        jdbcSetter.set(stmt, paramIdx, jsonDecoder.decode(value))
    }
}

/** Convenience class for defining concrete [LosslessFieldType] objects. */
abstract class SymmetricJdbcFieldType<T>(
    airbyteSchemaType: AirbyteSchemaType,
    jdbcAccessor: JdbcAccessor<T>,
    jsonCodec: JsonCodec<T>,
) :
    LosslessJdbcFieldType<T, T>(
        airbyteSchemaType,
        jdbcAccessor,
        jsonCodec,
        jsonCodec,
        jdbcAccessor
    )

data object BooleanFieldType :
    SymmetricJdbcFieldType<Boolean>(
        LeafAirbyteSchemaType.BOOLEAN,
        BooleanAccessor,
        BooleanCodec,
    )

data object BigDecimalFieldType :
    SymmetricJdbcFieldType<BigDecimal>(
        LeafAirbyteSchemaType.NUMBER,
        BigDecimalAccessor,
        BigDecimalCodec,
    )

data object DoubleFieldType :
    SymmetricJdbcFieldType<Double>(
        LeafAirbyteSchemaType.NUMBER,
        DoubleAccessor,
        DoubleCodec,
    )

data object FloatFieldType :
    SymmetricJdbcFieldType<Float>(
        LeafAirbyteSchemaType.NUMBER,
        FloatAccessor,
        FloatCodec,
    )

data object BigIntegerFieldType :
    SymmetricJdbcFieldType<BigDecimal>(
        LeafAirbyteSchemaType.INTEGER,
        BigDecimalAccessor,
        BigDecimalIntegerCodec,
    )

data object LongFieldType :
    SymmetricJdbcFieldType<Long>(
        LeafAirbyteSchemaType.INTEGER,
        LongAccessor,
        LongCodec,
    )

data object IntFieldType :
    SymmetricJdbcFieldType<Int>(
        LeafAirbyteSchemaType.INTEGER,
        IntAccessor,
        IntCodec,
    )

data object ShortFieldType :
    SymmetricJdbcFieldType<Short>(
        LeafAirbyteSchemaType.INTEGER,
        ShortAccessor,
        ShortCodec,
    )

data object ByteFieldType :
    SymmetricJdbcFieldType<Byte>(
        LeafAirbyteSchemaType.INTEGER,
        ByteAccessor,
        ByteCodec,
    )

data object StringFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        StringAccessor,
        TextCodec,
    )

data object NStringFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        NStringAccessor,
        TextCodec,
    )

data object CharacterStreamFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        CharacterStreamAccessor,
        TextCodec,
    )

data object NCharacterStreamFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        NCharacterStreamAccessor,
        TextCodec,
    )

data object ClobFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        ClobAccessor,
        TextCodec,
    )

data object NClobFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        NClobAccessor,
        TextCodec,
    )

data object XmlFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.STRING,
        XmlAccessor,
        TextCodec,
    )

data object UrlFieldType :
    SymmetricJdbcFieldType<URL>(
        LeafAirbyteSchemaType.STRING,
        UrlAccessor,
        UrlCodec,
    )

data object BytesFieldType :
    SymmetricJdbcFieldType<ByteBuffer>(
        LeafAirbyteSchemaType.BINARY,
        BytesAccessor,
        BinaryCodec,
    )

data object BinaryStreamFieldType :
    SymmetricJdbcFieldType<ByteBuffer>(
        LeafAirbyteSchemaType.BINARY,
        BinaryStreamAccessor,
        BinaryCodec,
    )

data object JsonStringFieldType :
    SymmetricJdbcFieldType<String>(
        LeafAirbyteSchemaType.JSONB,
        StringAccessor,
        JsonStringCodec,
    )

data object LocalDateFieldType :
    SymmetricJdbcFieldType<LocalDate>(
        LeafAirbyteSchemaType.DATE,
        DateAccessor,
        LocalDateCodec,
    )

data object LocalTimeFieldType :
    SymmetricJdbcFieldType<LocalTime>(
        LeafAirbyteSchemaType.TIME_WITHOUT_TIMEZONE,
        TimeAccessor,
        LocalTimeCodec,
    )

data object LocalDateTimeFieldType :
    SymmetricJdbcFieldType<LocalDateTime>(
        LeafAirbyteSchemaType.TIMESTAMP_WITHOUT_TIMEZONE,
        TimestampAccessor,
        LocalDateTimeCodec,
    )

data object OffsetTimeFieldType :
    LosslessJdbcFieldType<OffsetTime, OffsetTime>(
        LeafAirbyteSchemaType.TIME_WITH_TIMEZONE,
        ObjectGetter(OffsetTime::class.java),
        OffsetTimeCodec,
        OffsetTimeCodec,
        AnyAccessor,
    )

data object OffsetDateTimeFieldType :
    LosslessJdbcFieldType<OffsetDateTime, OffsetDateTime>(
        LeafAirbyteSchemaType.TIMESTAMP_WITH_TIMEZONE,
        ObjectGetter(OffsetDateTime::class.java),
        OffsetDateTimeCodec,
        OffsetDateTimeCodec,
        AnyAccessor,
    )

data object PokemonFieldType :
    JdbcFieldType<Any>(
        LeafAirbyteSchemaType.STRING,
        StringAccessor,
        AnyEncoder,
    )

data object NullFieldType :
    JdbcFieldType<Any?>(
        LeafAirbyteSchemaType.NULL,
        AnyAccessor,
        NullCodec,
    )

data class ArrayFieldType<T>(
    val elementFieldType: JdbcFieldType<T>,
) :
    JdbcFieldType<List<T>>(
        ArrayAirbyteSchemaType(elementFieldType.airbyteSchemaType),
        ArrayGetter(elementFieldType.jdbcGetter),
        ArrayEncoder(elementFieldType.jsonEncoder),
    )

data class SapHanaArrayFieldType<T>(
    val elementFieldType: JdbcFieldType<T>,
) :
    JdbcFieldType<List<T>>(
        ArrayAirbyteSchemaType(elementFieldType.airbyteSchemaType),
        SapHanaArrayGetter(elementFieldType),
        ArrayEncoder(elementFieldType.jsonEncoder),
    )
