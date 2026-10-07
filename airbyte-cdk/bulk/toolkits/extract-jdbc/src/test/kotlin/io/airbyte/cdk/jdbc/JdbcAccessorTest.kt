/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.jdbc

import io.airbyte.cdk.h2.H2TestFixture
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.math.BigDecimal
import java.nio.ByteBuffer
import java.sql.Connection
import java.sql.Date
import java.sql.JDBCType
import java.sql.PreparedStatement
import java.sql.ResultSet
import java.sql.SQLException
import java.sql.Statement
import java.sql.Timestamp
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.OffsetTime
import java.time.ZoneOffset
import java.util.stream.Stream
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class JdbcAccessorTest {
    val h2 = H2TestFixture()

    val columns =
        mapOf(
            "col_boolean" to "BOOLEAN",
            "col_number" to "DECFLOAT",
            "col_binary" to "VARBINARY",
            "col_clob" to "CLOB",
            "col_date" to "DATE",
            "col_time" to "TIME",
            "col_time_tz" to "TIME(6) WITH TIME ZONE",
            "col_timestamp" to "TIMESTAMP",
            "col_timestamp_tz" to "TIMESTAMP(6) WITH TIME ZONE",
            "col_array" to "INTEGER ARRAY[10]",
        )

    init {
        h2.execute(
            columns
                .map { "${it.key} ${it.value}" }
                .joinToString(", ", "CREATE TABLE datatypes (", ")"),
        )
    }

    @BeforeEach
    fun resetH2() {
        h2.execute("TRUNCATE TABLE datatypes")
        h2.execute(
            """
            INSERT INTO datatypes VALUES (
                TRUE,
                123,
                x'6D6E',
                'abcdef',
                '2024-03-01',
                '01:02:03',
                '01:02:03.456-04',
                '2024-03-01 01:02:03',
                '2024-03-01 01:02:03.456-04',
                ARRAY[1,2,3]
            )""",
        )
    }

    lateinit var columnName: String

    private fun <T> JdbcGetter<T>.select(): T? =
        h2.createConnection().use { conn: Connection ->
            conn.createStatement().use { stmt: Statement ->
                stmt.executeQuery("SELECT * FROM datatypes").use { rs: ResultSet ->
                    Assertions.assertTrue(rs.next())
                    val colIdx: Int = columns.keys.toList().indexOf(columnName) + 1
                    get(rs, colIdx)
                }
            }
        }

    private fun <T> JdbcSetter<T>.update(value: T) {
        val sql = "UPDATE datatypes SET $columnName = ?"
        h2.createConnection().use { conn: Connection ->
            conn.prepareStatement(sql).use { stmt: PreparedStatement ->
                set(stmt, 1, value)
                stmt.execute()
            }
        }
    }

    private fun updateToNull() {
        h2.createConnection().use { conn: Connection ->
            conn.createStatement().use { stmt: Statement ->
                stmt.execute("UPDATE datatypes SET $columnName = NULL")
            }
        }
    }

    @Test
    fun testBooleanAccessor() {
        columnName = "col_boolean"
        BooleanAccessor.run {
            Assertions.assertEquals(true, select())
            update(false)
            Assertions.assertEquals(false, select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testByteAccessor() {
        columnName = "col_number"
        ByteAccessor.run {
            Assertions.assertEquals(123, select())
            update(52)
            Assertions.assertEquals(52, select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testShortAccessor() {
        columnName = "col_number"
        ShortAccessor.run {
            Assertions.assertEquals(123, select())
            update(1234)
            Assertions.assertEquals(1234, select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testIntAccessor() {
        columnName = "col_number"
        IntAccessor.run {
            Assertions.assertEquals(123, select())
            update(123456)
            Assertions.assertEquals(123456, select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testLongAccessor() {
        columnName = "col_number"
        LongAccessor.run {
            Assertions.assertEquals(123L, select())
            update(1234567890123456L)
            Assertions.assertEquals(1234567890123456L, select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testFloatAccessor() {
        columnName = "col_number"
        FloatAccessor.run {
            Assertions.assertEquals(123f, select())
            update(123.456f)
            Assertions.assertEquals(123.456f, select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testDoubleAccessor() {
        columnName = "col_number"
        DoubleAccessor.run {
            Assertions.assertEquals(123.0, select())
            update(2.5)
            Assertions.assertEquals(2.5, select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testBigDecimalAccessor() {
        columnName = "col_number"
        BigDecimalAccessor.run {
            Assertions.assertEquals(0, BigDecimal("123").compareTo(select()))
            update(BigDecimal("0.0000000001"))
            Assertions.assertEquals(0, BigDecimal("0.0000000001").compareTo(select()))
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testBytesAccessor() {
        columnName = "col_binary"
        BytesAccessor.run {
            Assertions.assertEquals("mn", select()?.let { String(it.array()) })
            update(ByteBuffer.wrap("ab".toByteArray()))
            Assertions.assertEquals("ab", select()?.let { String(it.array()) })
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testBinaryStreamAccessor() {
        columnName = "col_binary"
        BinaryStreamAccessor.run {
            Assertions.assertEquals("mn", select()?.let { String(it.array()) })
            update(ByteBuffer.wrap("ab".toByteArray()))
            Assertions.assertEquals("ab", select()?.let { String(it.array()) })
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testClobAccessor() {
        columnName = "col_clob"
        ClobAccessor.run {
            Assertions.assertEquals("abcdef", select())
            update("ABCDEF")
            Assertions.assertEquals("ABCDEF", select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testNClobAccessor() {
        columnName = "col_clob"
        NClobAccessor.run {
            Assertions.assertEquals("abcdef", select())
            update("ABCDEF")
            Assertions.assertEquals("ABCDEF", select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testCharacterStreamAccessor() {
        columnName = "col_clob"
        CharacterStreamAccessor.run {
            Assertions.assertEquals("abcdef", select())
            update("ABCDEF")
            Assertions.assertEquals("ABCDEF", select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testNCharacterStreamAccessor() {
        columnName = "col_clob"
        NCharacterStreamAccessor.run {
            Assertions.assertEquals("abcdef", select())
            update("ABCDEF")
            Assertions.assertEquals("ABCDEF", select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testStringAccessor() {
        columnName = "col_clob"
        StringAccessor.run {
            Assertions.assertEquals("abcdef", select())
            update("ABCDEF")
            Assertions.assertEquals("ABCDEF", select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testNStringAccessor() {
        columnName = "col_clob"
        NStringAccessor.run {
            Assertions.assertEquals("abcdef", select())
            update("ABCDEF")
            Assertions.assertEquals("ABCDEF", select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testDateAccessor() {
        columnName = "col_date"
        DateAccessor.run {
            Assertions.assertEquals(LocalDate.of(2024, 3, 1), select())
            update(LocalDate.of(1999, 11, 12))
            Assertions.assertEquals(LocalDate.of(1999, 11, 12), select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @ParameterizedTest(name = "{0}")
    @MethodSource("temporalAccessorCases")
    fun testTemporalAccessors(case: TemporalAccessorCase) {
        val rs = mockk<ResultSet>()
        every { rs.getString(1) } returns "0000-00-00 00:00:00"
        case.stub(rs)
        every { rs.wasNull() } returns case.wasNull

        if (case.expectedException != null) {
            Assertions.assertThrows(case.expectedException) { case.getter.get(rs, 1) }
        } else {
            Assertions.assertEquals(case.expectedValue, case.getter.get(rs, 1))
        }

        verify(exactly = 0) { rs.getString(any<Int>()) }
    }

    data class TemporalAccessorCase(
        val name: String,
        val getter: JdbcGetter<*>,
        val stub: (ResultSet) -> Unit,
        val wasNull: Boolean,
        val expectedValue: Any? = null,
        val expectedException: Class<out Exception>? = null,
    ) {
        override fun toString(): String = name
    }

    companion object {
        @JvmStatic
        fun temporalAccessorCases(): Stream<Arguments> =
            Stream.of(
                Arguments.of(
                    TemporalAccessorCase(
                        "DateAccessor: driver returns null",
                        DateAccessor,
                        { rs -> every { rs.getDate(1) } returns null },
                        false,
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "DateAccessor: SQL NULL",
                        DateAccessor,
                        { rs -> every { rs.getDate(1) } returns Date.valueOf("2024-03-01") },
                        true,
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "DateAccessor: normal value",
                        DateAccessor,
                        { rs -> every { rs.getDate(1) } returns Date.valueOf("2024-03-01") },
                        false,
                        LocalDate.of(2024, 3, 1),
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "DateAccessor: unconvertible value",
                        DateAccessor,
                        { rs ->
                            every { rs.getDate(1) } throws
                                SQLException(
                                    "Value '2026-00-01' can not be represented as java.sql.Timestamp",
                                )
                        },
                        false,
                        expectedException = SQLException::class.java,
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "TimestampAccessor: driver returns null",
                        TimestampAccessor,
                        { rs -> every { rs.getTimestamp(1) } returns null },
                        false,
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "TimestampAccessor: SQL NULL",
                        TimestampAccessor,
                        { rs -> every { rs.getTimestamp(1) } returns Timestamp(0) },
                        true,
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "TimestampAccessor: normal value",
                        TimestampAccessor,
                        { rs ->
                            every { rs.getTimestamp(1) } returns
                                Timestamp.valueOf("2024-03-01 01:02:03")
                        },
                        false,
                        LocalDateTime.of(2024, 3, 1, 1, 2, 3),
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "TimestampAccessor: unconvertible value",
                        TimestampAccessor,
                        { rs ->
                            every { rs.getTimestamp(1) } throws
                                SQLException(
                                    "Value '2026-00-01' can not be represented as java.sql.Timestamp",
                                )
                        },
                        false,
                        expectedException = SQLException::class.java,
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "OffsetDateTimeFieldType: driver returns null",
                        OffsetDateTimeFieldType.jdbcGetter,
                        { rs -> every { rs.getObject(1, OffsetDateTime::class.java) } returns null },
                        false,
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "OffsetDateTimeFieldType: SQL NULL",
                        OffsetDateTimeFieldType.jdbcGetter,
                        { rs ->
                            every { rs.getObject(1, OffsetDateTime::class.java) } returns
                                OffsetDateTime.of(2024, 3, 1, 1, 2, 3, 0, ZoneOffset.UTC)
                        },
                        true,
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "OffsetDateTimeFieldType: normal value",
                        OffsetDateTimeFieldType.jdbcGetter,
                        { rs ->
                            every { rs.getObject(1, OffsetDateTime::class.java) } returns
                                OffsetDateTime.of(2024, 3, 1, 1, 2, 3, 0, ZoneOffset.UTC)
                        },
                        false,
                        OffsetDateTime.of(2024, 3, 1, 1, 2, 3, 0, ZoneOffset.UTC),
                    ),
                ),
                Arguments.of(
                    TemporalAccessorCase(
                        "OffsetDateTimeFieldType: unconvertible value",
                        OffsetDateTimeFieldType.jdbcGetter,
                        { rs ->
                            every { rs.getObject(1, OffsetDateTime::class.java) } throws
                                SQLException(
                                    "Value '2026-00-01' can not be represented as java.sql.Timestamp",
                                )
                        },
                        false,
                        expectedException = SQLException::class.java,
                    ),
                ),
            )
    }

    @Test
    fun testTimeAccessor() {
        columnName = "col_time"
        TimeAccessor.run {
            Assertions.assertEquals(LocalTime.of(1, 2, 3), select())
            update(LocalTime.of(11, 12, 13))
            Assertions.assertEquals(LocalTime.of(11, 12, 13), select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testTimestampAccessor() {
        columnName = "col_timestamp"
        TimestampAccessor.run {
            Assertions.assertEquals(LocalDateTime.of(2024, 3, 1, 1, 2, 3), select())
            update(LocalDateTime.of(1999, 11, 12, 11, 12, 13))
            Assertions.assertEquals(LocalDateTime.of(1999, 11, 12, 11, 12, 13), select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testOffsetDateTimeFieldTypeGetter() {
        columnName = "col_timestamp_tz"
        OffsetDateTimeFieldType.jdbcGetter.run {
            Assertions.assertEquals(
                OffsetDateTime.of(2024, 3, 1, 1, 2, 3, 456000000, ZoneOffset.ofHours(-4)),
                select(),
            )
            updateToNull()
            Assertions.assertNull(select())
        }
    }

    @Test
    fun testObjectGetterAnySetter() {
        columnName = "col_time_tz"
        ObjectGetter(OffsetTime::class.java).run {
            Assertions.assertEquals(
                OffsetTime.of(1, 2, 3, 456000000, ZoneOffset.ofHours(-4)),
                select(),
            )
        }
        AnySetter(JDBCType.TIME_WITH_TIMEZONE.vendorTypeNumber).run {
            update(OffsetTime.of(11, 12, 13, 456000000, ZoneOffset.ofHours(3)))
        }
        AnyAccessor.run {
            Assertions.assertEquals(
                OffsetTime.of(11, 12, 13, 456000000, ZoneOffset.ofHours(3)),
                select(),
            )
        }
        columnName = "col_timestamp_tz"
        ObjectGetter(OffsetDateTime::class.java).run {
            Assertions.assertEquals(
                OffsetDateTime.of(2024, 3, 1, 1, 2, 3, 456000000, ZoneOffset.ofHours(-4)),
                select(),
            )
        }
    }

    @Test
    @Suppress("DEPRECATION")
    fun testAnyAccessor() {
        columnName = "col_date"
        AnyAccessor.run {
            Assertions.assertEquals(Date(124, 2, 1), select())
            update(Date(99, 10, 12))
            Assertions.assertEquals(Date(99, 10, 12), select())
            updateToNull()
            Assertions.assertEquals(null, select())
        }
    }

    @Test
    fun testArrayGetterAndSetter() {
        columnName = "col_array"
        ArrayGetter(IntAccessor).run { Assertions.assertEquals(listOf(1, 2, 3), select()) }
        ArraySetter("INTEGER").run { update(listOf(4, 5)) }
        ArrayGetter(IntAccessor).run { Assertions.assertEquals(listOf(4, 5), select()) }
        updateToNull()
        ArrayGetter(IntAccessor).run { Assertions.assertEquals(null, select()) }
    }
}
