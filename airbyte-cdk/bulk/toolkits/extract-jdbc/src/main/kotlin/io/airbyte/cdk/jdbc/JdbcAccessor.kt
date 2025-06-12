/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

import java.io.ByteArrayInputStream
import java.math.BigDecimal
import java.net.URL
import java.nio.ByteBuffer
import java.sql.Clob
import java.sql.Date
import java.sql.NClob
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.Time
import java.sql.Timestamp
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime

/** Combination of [JdbcGetter] and [JdbcSetter]. */
interface JdbcAccessor<T> : JdbcGetter<T>, JdbcSetter<T>

/**
 * Thin wrapper around [ResultSet] get* methods, e.g. [ResultSet.getString].
 *
 * The caller owns the return value, which is not bound to the transaction. The implementation
 * handles calling [ResultSet.wasNull].
 */
fun interface JdbcGetter<T> {
    fun get(
        rs: ResultSet,
        colIdx: Int,
    ): T?
}

/**
 * Thin wrapper around [PreparedStatement] set* methods, e.g. [PreparedStatement.setString].
 *
 * The implementation takes ownership of the argument [value]. The type parameter [T] is typically
 * not nullable as we have no use for [PreparedStatement.setNull] for the queries that we run.
 */
fun interface JdbcSetter<T> {
    fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: T,
    )
}

data object BooleanAccessor : JdbcAccessor<Boolean> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): Boolean? = rs.getBoolean(colIdx).takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Boolean,
    ) {
        stmt.setBoolean(paramIdx, value)
    }
}

data object ByteAccessor : JdbcAccessor<Byte> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): Byte? = rs.getByte(colIdx).takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Byte,
    ) {
        stmt.setByte(paramIdx, value)
    }
}

data object ShortAccessor : JdbcAccessor<Short> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): Short? = rs.getShort(colIdx).takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Short,
    ) {
        stmt.setShort(paramIdx, value)
    }
}

data object IntAccessor : JdbcAccessor<Int> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): Int? = rs.getInt(colIdx).takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Int,
    ) {
        stmt.setInt(paramIdx, value)
    }
}

data object LongAccessor : JdbcAccessor<Long> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): Long? = rs.getLong(colIdx).takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Long,
    ) {
        stmt.setLong(paramIdx, value)
    }
}

data object FloatAccessor : JdbcAccessor<Float> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): Float? = rs.getFloat(colIdx).takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Float,
    ) {
        stmt.setFloat(paramIdx, value)
    }
}

data object DoubleAccessor : JdbcAccessor<Double> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): Double? = rs.getDouble(colIdx).takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Double,
    ) {
        stmt.setDouble(paramIdx, value)
    }
}

data object BigDecimalAccessor : JdbcAccessor<BigDecimal> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): BigDecimal? = rs.getBigDecimal(colIdx)?.takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: BigDecimal,
    ) {
        stmt.setBigDecimal(paramIdx, value)
    }
}

/**
 * [BytesAccessor] uses a [ByteBuffer] instead of a [ByteArray] so that Micronaut doesn't go crazy.
 */
data object BytesAccessor : JdbcAccessor<ByteBuffer> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): ByteBuffer? = rs.getBytes(colIdx)?.takeUnless { rs.wasNull() }?.let(ByteBuffer::wrap)

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: ByteBuffer,
    ) {
        stmt.setBytes(paramIdx, value.array())
    }
}

/**
 * [BinaryStreamAccessor] uses a [ByteBuffer] instead of a [ByteArray] so that Micronaut doesn't go
 * crazy.
 */
data object BinaryStreamAccessor : JdbcAccessor<ByteBuffer> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): ByteBuffer? =
        rs.getBinaryStream(colIdx)
            ?.takeUnless { rs.wasNull() }
            ?.use { ByteBuffer.wrap(it.readAllBytes()) }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: ByteBuffer,
    ) {
        stmt.setBinaryStream(paramIdx, ByteArrayInputStream(value.array()))
    }
}

data object ClobAccessor : JdbcAccessor<String> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): String? {
        val clob: Clob = rs.getClob(colIdx)?.takeUnless { rs.wasNull() } ?: return null
        return clob.getSubString(1, clob.length().toInt())
    }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: String,
    ) {
        stmt.setString(paramIdx, value)
    }
}

data object NClobAccessor : JdbcAccessor<String> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): String? {
        val nclob: NClob = rs.getNClob(colIdx)?.takeUnless { rs.wasNull() } ?: return null
        return nclob.getSubString(1, nclob.length().toInt())
    }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: String,
    ) {
        stmt.setString(paramIdx, value)
    }
}

data object CharacterStreamAccessor : JdbcAccessor<String> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): String? = rs.getCharacterStream(colIdx)?.takeUnless { rs.wasNull() }?.use { it.readText() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: String,
    ) {
        stmt.setString(paramIdx, value)
    }
}

data object NCharacterStreamAccessor : JdbcAccessor<String> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): String? = rs.getNCharacterStream(colIdx)?.takeUnless { rs.wasNull() }?.use { it.readText() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: String,
    ) {
        stmt.setString(paramIdx, value)
    }
}

data object StringAccessor : JdbcAccessor<String> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): String? = rs.getString(colIdx)?.takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: String,
    ) {
        stmt.setString(paramIdx, value)
    }
}

data object NStringAccessor : JdbcAccessor<String> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): String? = rs.getNString(colIdx)?.takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: String,
    ) {
        stmt.setNString(paramIdx, value)
    }
}

data object DateAccessor : JdbcAccessor<LocalDate> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): LocalDate? = rs.getDate(colIdx)?.takeUnless { rs.wasNull() }?.toLocalDate()

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: LocalDate,
    ) {
        stmt.setDate(paramIdx, Date.valueOf(value))
    }
}

data object TimeAccessor : JdbcAccessor<LocalTime> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): LocalTime? = rs.getTime(colIdx)?.takeUnless { rs.wasNull() }?.toLocalTime()

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: LocalTime,
    ) {
        stmt.setTime(paramIdx, Time.valueOf(value))
    }
}

data object TimestampAccessor : JdbcAccessor<LocalDateTime> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): LocalDateTime? = rs.getTimestamp(colIdx)?.takeUnless { rs.wasNull() }?.toLocalDateTime()

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: LocalDateTime,
    ) {
        stmt.setTimestamp(paramIdx, Timestamp.valueOf(value))
    }
}

data object XmlAccessor : JdbcAccessor<String> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): String? = rs.getSQLXML(colIdx)?.takeUnless { rs.wasNull() }?.string

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: String,
    ) {
        stmt.setString(paramIdx, value)
    }
}

data object UrlAccessor : JdbcAccessor<URL> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): URL? = rs.getURL(colIdx)?.takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: URL,
    ) {
        stmt.setURL(paramIdx, value)
    }
}

data class ObjectGetter<T>(
    val type: Class<T>,
) : JdbcGetter<T> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): T? = rs.getObject(colIdx, type)?.takeUnless { rs.wasNull() }
}

data object AnyAccessor : JdbcAccessor<Any> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): Any? = rs.getObject(colIdx)?.takeUnless { rs.wasNull() }

    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Any,
    ) {
        stmt.setObject(paramIdx, value)
    }
}

data class AnySetter(
    val sqlType: Int,
) : JdbcSetter<Any> {
    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: Any,
    ) {
        stmt.setObject(paramIdx, value, sqlType)
    }
}

data class ArrayGetter<T>(
    val elementGetter: JdbcGetter<T>,
) : JdbcGetter<List<T>> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): List<T>? =
        rs.getArray(colIdx)
            ?.takeUnless { rs.wasNull() }
            ?.resultSet
            ?.use { rsInner: ResultSet ->
                mutableListOf<T>().apply {
                    while (rsInner.next()) {
                        addLast(elementGetter.get(rsInner, 2))
                    }
                }
            }
}

data class ArraySetter(
    val elementSqlTypeName: String,
) : JdbcSetter<List<Any?>> {
    override fun set(
        stmt: PreparedStatement,
        paramIdx: Int,
        value: List<Any?>,
    ) {
        val javaArray: Array<Any?> = value.toTypedArray<Any?>()
        stmt.setArray(paramIdx, stmt.connection.createArrayOf(elementSqlTypeName, javaArray))
    }
}

@Suppress("UNCHECKED_CAST")
data class SapHanaArrayGetter<T>(
    val elementFieldType: JdbcFieldType<T>,
) : JdbcGetter<List<T>> {
    override fun get(
        rs: ResultSet,
        colIdx: Int,
    ): List<T>? =
        rs.getArray(colIdx)
            ?.takeUnless { rs.wasNull() }
            ?.let { array ->
                val arrayValue = array.array as Array<*>
                convertArrayToList(arrayValue, elementFieldType.genericClass)
            }

    private fun <T> convertArrayToList(array: Array<*>, targetClass: Class<T>): List<T> {
        return when {
            targetClass == LocalDate::class.java -> {
                array.map { dateValue ->
                    when (dateValue) {
                        is Date -> dateValue.toLocalDate()
                        else ->
                            throw IllegalArgumentException(
                                "Cannot convert ${dateValue?.javaClass} to LocalDate"
                            )
                    }
                } as List<T>
            }
            targetClass == LocalTime::class.java -> {
                array.map { dateValue ->
                    when (dateValue) {
                        is Time -> dateValue.toLocalTime()
                        else ->
                            throw IllegalArgumentException(
                                "Cannot convert ${dateValue?.javaClass} to LocalTime"
                            )
                    }
                } as List<T>
            }
            targetClass == LocalDateTime::class.java -> {
                array.map { dateValue ->
                    when (dateValue) {
                        is Timestamp -> dateValue.toLocalDateTime()
                        else ->
                            throw IllegalArgumentException(
                                "Cannot convert ${dateValue?.javaClass} to LocalDateTime"
                            )
                    }
                } as List<T>
            }
            else ->
                array.map { value ->
                    targetClass.cast(value)
                        ?: throw IllegalArgumentException(
                            "Cannot convert ${value?.javaClass} to ${targetClass.simpleName}"
                        )
                }
        }
    }
}
