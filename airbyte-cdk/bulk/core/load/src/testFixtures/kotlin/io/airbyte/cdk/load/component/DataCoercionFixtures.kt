/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import java.math.BigDecimal
import java.math.BigInteger
import java.time.LocalDate
import java.time.LocalDateTime
import java.time.OffsetDateTime
import java.time.format.DateTimeFormatter
import java.time.format.DateTimeFormatterBuilder
import java.time.format.SignStyle
import java.time.temporal.ChronoField
import org.junit.jupiter.params.provider.Arguments

/*
 * This file defines "interesting values" for all data types, along with expected behavior for those values.
 * You're free to define your own values/behavior depending on the destination, but it's recommended
 * that you try to match behavior to an existing fixture.
 *
 * Classes also include some convenience functions for JUnit. For example, you could annotate your
 * method with:
 * ```kotlin
 * @ParameterizedTest
 * @MethodSource("io.airbyte.cdk.load.component.DataCoercionIntegerFixtures#int64")
 * ```
 *
 * By convention, all fixtures are declared as:
 * 1. One or more `val <name>: List<Pair<AirbyteValue, Any?>>` (each pair representing the input value,
 *    and the expected output value)
 * 2. One or more `fun <name>(): List<Arguments> = <name>.toArgs()`, which can be provided to JUnit's MethodSource
 *
 * If you need to mutate fixtures in some way, you should reference the `val`, and use the `toArgs()`
 * extension function to convert it to JUnit's Arguments class. See [DataCoercionIntegerFixtures.int64AsBigInteger]
 * for an example.
 */

object DataCoercionIntegerFixtures {
    // "9".repeat(38)
    val numeric38_0Max = bigint("99999999999999999999999999999999999999")
    val numeric38_0Min = bigint("-99999999999999999999999999999999999999")

    /**
     * Many destinations use int64 to represent integers. In this case, we null out any value beyond
     * Long.MIN/MAX_VALUE.
     */
    val int64 =
        listOf(
            test("0", IntegerValue(0), 0L),
            test("1", IntegerValue(1), 1L),
            test("-1", IntegerValue(-1), -1L),
            test("42", IntegerValue(42), 42L),
            test("-42", IntegerValue(-42), -42L),
            // int32 bounds, and slightly out of bounds
            test("int32 max", IntegerValue(Integer.MAX_VALUE.toLong()), Integer.MAX_VALUE.toLong()),
            test("int32 min", IntegerValue(Integer.MIN_VALUE.toLong()), Integer.MIN_VALUE.toLong()),
            test(
                "int32_max + 1",
                IntegerValue(Integer.MAX_VALUE.toLong() + 1),
                Integer.MAX_VALUE.toLong() + 1
            ),
            test(
                "int32_min - 1",
                IntegerValue(Integer.MIN_VALUE.toLong() - 1),
                Integer.MIN_VALUE.toLong() - 1
            ),
            // int64 bounds, and slightly out of bounds
            test("int64 max", IntegerValue(Long.MAX_VALUE), Long.MAX_VALUE),
            test("int64 min", IntegerValue(Long.MIN_VALUE), Long.MIN_VALUE),
            // values out of int64 bounds are nulled
            test(
                "int64_max + 1",
                IntegerValue(bigint(Long.MAX_VALUE) + BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "int64_min - 1",
                IntegerValue(bigint(Long.MIN_VALUE) - BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            // NUMERIC(38, 9) bounds, and slightly out of bounds
            // (these are all out of bounds for an int64 value, so they all get nulled)
            test(
                "numeric(38,0) max",
                IntegerValue(numeric38_0Max),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "numeric(38,0) min",
                IntegerValue(numeric38_0Min),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "numeric(38,0)_max + 1",
                IntegerValue(numeric38_0Max + BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "numeric(38,0)_min - 1",
                IntegerValue(numeric38_0Min - BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
        )

    /**
     * Many destination warehouses represent integers as a fixed-point type with 38 digits of
     * precision. In this case, we only need to null out numbers larger than `1e38 - 1` / smaller
     * than `-1e38 + 1`.
     */
    val numeric38_0 =
        listOf(
            test("0", IntegerValue(0), bigint(0L)),
            test("1", IntegerValue(1), bigint(1L)),
            test("-1", IntegerValue(-1), bigint(-1L)),
            test("42", IntegerValue(42), bigint(42L)),
            test("-42", IntegerValue(-42), bigint(-42L)),
            // int32 bounds, and slightly out of bounds
            test(
                "int32 max",
                IntegerValue(Integer.MAX_VALUE.toLong()),
                bigint(Integer.MAX_VALUE.toLong())
            ),
            test(
                "int32 min",
                IntegerValue(Integer.MIN_VALUE.toLong()),
                bigint(Integer.MIN_VALUE.toLong())
            ),
            test(
                "int32_max + 1",
                IntegerValue(Integer.MAX_VALUE.toLong() + 1),
                bigint(Integer.MAX_VALUE.toLong() + 1)
            ),
            test(
                "int32_min - 1",
                IntegerValue(Integer.MIN_VALUE.toLong() - 1),
                bigint(Integer.MIN_VALUE.toLong() - 1)
            ),
            // int64 bounds, and slightly out of bounds
            test("int64 max", IntegerValue(Long.MAX_VALUE), bigint(Long.MAX_VALUE)),
            test("int64 min", IntegerValue(Long.MIN_VALUE), bigint(Long.MIN_VALUE)),
            test(
                "int64_max + 1",
                IntegerValue(bigint(Long.MAX_VALUE) + BigInteger.ONE),
                bigint(Long.MAX_VALUE) + BigInteger.ONE
            ),
            test(
                "int64_min - 1",
                IntegerValue(bigint(Long.MIN_VALUE) - BigInteger.ONE),
                bigint(Long.MIN_VALUE) - BigInteger.ONE
            ),
            // NUMERIC(38, 9) bounds, and slightly out of bounds
            test("numeric(38,0) max", IntegerValue(numeric38_0Max), numeric38_0Max),
            test("numeric(38,0) min", IntegerValue(numeric38_0Min), numeric38_0Min),
            // These values exceed the 38-digit range, so they get nulled out
            test(
                "numeric(38,0)_max + 1",
                IntegerValue(numeric38_0Max + BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "numeric(38,0)_min - 1",
                IntegerValue(numeric38_0Min - BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
        )

    @JvmStatic fun int64() = int64.toArgs()

    /**
     * Convenience fixture if your [TestTableOperationsClient] returns integers as [BigInteger]
     * rather than [Long].
     */
    @JvmStatic
    fun int64AsBigInteger() =
        int64.map { it.copy(outputValue = it.outputValue?.let { bigint(it as Long) }) }

    /**
     * Convenience fixture if your [TestTableOperationsClient] returns integers as [BigDecimal]
     * rather than [Long].
     */
    @JvmStatic
    fun int64AsBigDecimal() =
        int64.map { it.copy(outputValue = it.outputValue?.let { BigDecimal.valueOf(it as Long) }) }

    @JvmStatic fun numeric38_0() = numeric38_0.toArgs()
}

object DataCoercionNumberFixtures {
    val numeric38_9Max = bigdec("99999999999999999999999999999.999999999")
    val numeric38_9Min = bigdec("-99999999999999999999999999999.999999999")

    val float64 =
        listOf(
            test("0", NumberValue(bigdec(0)), 0.0),
            test("1", NumberValue(bigdec(1)), 1.0),
            test("-1", NumberValue(bigdec(-1)), -1.0),
            // This value isn't exactly representable as a float64
            // (the exact value is `123.400000000000005684341886080801486968994140625`)
            // but we should preserve the canonical representation
            test("123.4", NumberValue(bigdec("123.4")), 123.4),
            test("-123.4", NumberValue(bigdec("-123.4")), -123.4),
            // These values have too much precision for a float64, so we round them
            // TODO snowflake rounds these differently than expected, figure out why. Or make it
            // easier for snowflake to override specific entries in this list.
            test(
                "positive high-precision float",
                NumberValue(bigdec("1234567890.1234567890123456789")),
                1234567890.1234567,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "negative high-precision float",
                NumberValue(bigdec("-1234567890.1234567890123456789")),
                -1234567890.1234567,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "numeric(38,9) max",
                NumberValue(numeric38_9Max),
                1.0E29,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "numeric(38,9) min",
                NumberValue(numeric38_9Min),
                -1.0E29,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            // min/max_value are all positive values, so we need to manually test their negative
            // version
            test(
                "smallest positive float32",
                NumberValue(bigdec(Float.MIN_VALUE.toDouble())),
                Float.MIN_VALUE.toDouble()
            ),
            test(
                "smallest negative float32",
                NumberValue(bigdec(-Float.MIN_VALUE.toDouble())),
                -Float.MIN_VALUE.toDouble()
            ),
            test(
                "largest positive float32",
                NumberValue(bigdec(Float.MAX_VALUE.toDouble())),
                Float.MAX_VALUE.toDouble()
            ),
            test(
                "largest negative float32",
                NumberValue(bigdec(-Float.MAX_VALUE.toDouble())),
                -Float.MAX_VALUE.toDouble()
            ),
            test(
                "smallest positive float64",
                NumberValue(bigdec(Double.MIN_VALUE)),
                Double.MIN_VALUE
            ),
            test(
                "smallest negative float64",
                NumberValue(bigdec(-Double.MIN_VALUE)),
                -Double.MIN_VALUE
            ),
            // TODO snowflake writes this value correctly, but reads it back as infinity. Need to
            // fix SnowflakeTestOperationClient
            test(
                "largest positive float64",
                NumberValue(bigdec(Double.MAX_VALUE)),
                Double.MAX_VALUE
            ),
            test(
                "largest negative float64",
                NumberValue(bigdec(-Double.MAX_VALUE)),
                -Double.MAX_VALUE
            ),
            // These values are out of bounds, so we null them
            test(
                "slightly above largest positive float64",
                NumberValue(bigdec(Double.MAX_VALUE) + bigdec(Double.MIN_VALUE)),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            test(
                "slightly below largest negative float64",
                NumberValue(bigdec(-Double.MAX_VALUE) - bigdec(Double.MIN_VALUE)),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
        )

    val numeric38_9 =
        listOf(
                test("0", NumberValue(bigdec(0)), bigdec(0.0)),
                test("1", NumberValue(bigdec(1)), bigdec(1.0)),
                test("-1", NumberValue(bigdec(-1)), bigdec(-1.0)),
                // This value isn't exactly representable as a float64
                // (the exact value is `123.400000000000005684341886080801486968994140625`)
                // but it's perfectly fine as a numeric(38, 9)
                test("123.4", NumberValue(bigdec("123.4")), bigdec("123.4")),
                test("-123.4", NumberValue(bigdec("-123.4")), bigdec("-123.4")),
                // These values have too much precision for a numeric(38, 9), so we round them
                test(
                    "positive high-precision float",
                    NumberValue(bigdec("1234567890.1234567890123456789")),
                    bigdec("1234567890.123456789"),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "negative high-precision float",
                    NumberValue(bigdec("-1234567890.1234567890123456789")),
                    bigdec("-1234567890.123456789"),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "smallest positive float32",
                    NumberValue(bigdec(Float.MIN_VALUE.toDouble())),
                    bigdec(0),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "smallest negative float32",
                    NumberValue(bigdec(-Float.MIN_VALUE.toDouble())),
                    bigdec(0),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "smallest positive float64",
                    NumberValue(bigdec(Double.MIN_VALUE)),
                    bigdec(0),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "smallest negative float64",
                    NumberValue(bigdec(-Double.MIN_VALUE)),
                    bigdec(0),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                // numeric bounds are perfectly fine
                test("numeric(38,9) max", NumberValue(numeric38_9Max), numeric38_9Max),
                test("numeric(38,9) min", NumberValue(numeric38_9Min), numeric38_9Min),
                // These values are out of bounds, so we null them
                test(
                    "largest positive float32",
                    NumberValue(bigdec(Float.MAX_VALUE.toDouble())),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "largest negative float32",
                    NumberValue(bigdec(-Float.MAX_VALUE.toDouble())),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "largest positive float64",
                    NumberValue(bigdec(Double.MAX_VALUE)),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "largest negative float64",
                    NumberValue(bigdec(-Double.MAX_VALUE)),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "slightly above largest positive float64",
                    NumberValue(bigdec(Double.MAX_VALUE) + bigdec(Double.MIN_VALUE)),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                test(
                    "slightly below largest negative float64",
                    NumberValue(bigdec(-Double.MAX_VALUE) - bigdec(Double.MIN_VALUE)),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
            )
            .map { it.copy(outputValue = (it.outputValue as BigDecimal?)?.setScale(9)) }

    @JvmStatic fun float64() = float64.toArgs()
    @JvmStatic fun numeric38_9() = numeric38_9.toArgs()
}

const val SIMPLE_TIMESTAMP = "simple timestamp"
const val UNIX_EPOCH = "unix epoch"
const val MINIMUM_TIMESTAMP = "minimum timestamp"
const val MAXIMUM_TIMESTAMP = "maximum timestamp"
const val OUT_OF_RANGE_TIMESTAMP = "out of range timestamp"
const val HIGH_PRECISION_TIMESTAMP = "high-precision timestamp"

object DataCoercionTimestampTzFixtures {
    /**
     * Many warehouses support timestamps between years 0001 - 9999.
     *
     * Depending on the exact warehouse, you may need to tweak the precision on some values. For
     * example, Snowflake supports nanoseconds-precision timestamps (9 decimal points), but Bigquery
     * only supports microseconds-precision (6 decimal points). Bigquery would probably do something
     * like:
     * ```kotlin
     * DataCoercionNumberFixtures.traditionalWarehouse
     *   .map {
     *     when (it.name) {
     *       "maximum AD timestamp" -> it.copy(
     *         inputValue = TimestampWithTimezoneValue("9999-12-31T23:59:59.999999Z"),
     *         outputValue = OffsetDateTime.parse("9999-12-31T23:59:59.999999Z"),
     *         changeReason = Reason.DESTINATION_FIELD_SIZE_LIMITATION,
     *       )
     *       "high-precision timestamp" -> it.copy(
     *         outputValue = OffsetDateTime.parse("2025-01-23T01:01:00.123456Z"),
     *         changeReason = Reason.DESTINATION_FIELD_SIZE_LIMITATION,
     *       )
     *     }
     *   }
     * ```
     */
    val commonWarehouse =
        listOf(
            test(
                SIMPLE_TIMESTAMP,
                TimestampWithTimezoneValue("2025-01-23T12:34:56.789Z"),
                "2025-01-23T12:34:56.789Z",
            ),
            test(
                UNIX_EPOCH,
                TimestampWithTimezoneValue("1970-01-01T00:00:00Z"),
                "1970-01-01T00:00:00Z",
            ),
            test(
                MINIMUM_TIMESTAMP,
                TimestampWithTimezoneValue("0001-01-01T00:00:00Z"),
                "0001-01-01T00:00:00Z",
            ),
            test(
                MAXIMUM_TIMESTAMP,
                TimestampWithTimezoneValue("9999-12-31T23:59:59.999999999Z"),
                "9999-12-31T23:59:59.999999999Z",
            ),
            test(
                OUT_OF_RANGE_TIMESTAMP,
                TimestampWithTimezoneValue(odt("10000-01-01T00:00Z")),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            ),
            test(
                HIGH_PRECISION_TIMESTAMP,
                TimestampWithTimezoneValue("2025-01-23T01:01:00.123456789Z"),
                "2025-01-23T01:01:00.123456789Z",
            ),
        )

    @JvmStatic fun commonWarehouse() = commonWarehouse.toArgs()
}

object DataCoercionTimestampNtzFixtures {
    /** See [DataCoercionTimestampTzFixtures.commonWarehouse] for explanation */
    val commonWarehouse =
        listOf(
            test(
                SIMPLE_TIMESTAMP,
                TimestampWithoutTimezoneValue("2025-01-23T12:34:56.789"),
                "2025-01-23T12:34:56.789",
            ),
            test(
                UNIX_EPOCH,
                TimestampWithoutTimezoneValue("1970-01-01T00:00:00"),
                "1970-01-01T00:00:00",
            ),
            test(
                MINIMUM_TIMESTAMP,
                TimestampWithoutTimezoneValue("0001-01-01T00:00:00"),
                "0001-01-01T00:00:00",
            ),
            test(
                MAXIMUM_TIMESTAMP,
                TimestampWithoutTimezoneValue("9999-12-31T23:59:59.999999999"),
                "9999-12-31T23:59:59.999999999",
            ),
            test(
                OUT_OF_RANGE_TIMESTAMP,
                TimestampWithoutTimezoneValue(ldt("10000-01-01T00:00")),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            ),
            test(
                HIGH_PRECISION_TIMESTAMP,
                TimestampWithoutTimezoneValue("2025-01-23T01:01:00.123456789"),
                "2025-01-23T01:01:00.123456789",
            ),
        )

    @JvmStatic fun commonWarehouse() = commonWarehouse.toArgs()
}

const val MIDNIGHT = "midnight"
const val MAX_TIME = "max time"
const val HIGH_NOON = "high noon"

object DataCoercionTimeTzFixtures {
    val timetz =
        listOf(
            test(MIDNIGHT, TimeWithTimezoneValue("00:00Z"), "00:00Z"),
            test(MAX_TIME, TimeWithTimezoneValue("23:59:59.999999999Z"), "23:59:59.999999999Z"),
            test(HIGH_NOON, TimeWithTimezoneValue("12:00Z"), "12:00Z"),
        )

    @JvmStatic fun timetz() = timetz.toArgs()
}

object DataCoercionTimeNtzFixtures {
    val timentz =
        listOf(
            test(MIDNIGHT, TimeWithoutTimezoneValue("00:00"), "00:00"),
            test(MAX_TIME, TimeWithoutTimezoneValue("23:59:59.999999999"), "23:59:59.999999999"),
            test(HIGH_NOON, TimeWithoutTimezoneValue("12:00"), "12:00"),
        )

    @JvmStatic fun timentz() = timentz.toArgs()
}

object DataCoercionDateFixtures {
    val commonWarehouse =
        listOf(
            test(
                SIMPLE_TIMESTAMP,
                DateValue("2025-01-23"),
                "2025-01-23",
            ),
            test(
                UNIX_EPOCH,
                DateValue("1970-01-01"),
                "1970-01-01",
            ),
            test(
                MINIMUM_TIMESTAMP,
                DateValue("0001-01-01"),
                "0001-01-01",
            ),
            test(
                MAXIMUM_TIMESTAMP,
                DateValue("9999-12-31"),
                "9999-12-31",
            ),
            test(
                OUT_OF_RANGE_TIMESTAMP,
                DateValue(date("10000-01-01")),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            ),
        )

    @JvmStatic fun commonWarehouse() = commonWarehouse.toArgs()
}

fun List<DataCoercionFixture>.toArgs(): List<Arguments> =
    this.map { Arguments.argumentSet(it.name, it.inputValue, it.outputValue, it.changeReason) }
        .toList()

/**
 * Utility method to use the BigDecimal constructor (supports exponential notation like `1e38`) to
 * construct a BigInteger.
 */
fun bigint(str: String): BigInteger = BigDecimal(str).toBigIntegerExact()

/** Shorthand utility method to construct a bigint from a long */
fun bigint(long: Long): BigInteger = BigInteger.valueOf(long)

fun bigdec(str: String): BigDecimal = BigDecimal(str)

fun bigdec(double: Double): BigDecimal = BigDecimal.valueOf(double)

fun bigdec(int: Int): BigDecimal = BigDecimal.valueOf(int.toDouble())

fun odt(str: String): OffsetDateTime = OffsetDateTime.parse(str, dateTimeFormatter)

fun ldt(str: String): LocalDateTime = LocalDateTime.parse(str, dateTimeFormatter)

fun date(str: String): LocalDate = LocalDate.parse(str, dateFormatter)

// The default java.time.*.parse() behavior only accepts up to 4-digit years.
// Build a custom formatter to handle larger years.
val dateFormatter =
    DateTimeFormatterBuilder()
        // java.time.* supports up to 9-digit years
        .appendValue(ChronoField.YEAR, 1, 9, SignStyle.NORMAL)
        .appendLiteral('-')
        .appendValue(ChronoField.MONTH_OF_YEAR)
        .appendLiteral('-')
        .appendValue(ChronoField.DAY_OF_MONTH)
        .toFormatter()

val dateTimeFormatter =
    DateTimeFormatterBuilder()
        .append(dateFormatter)
        .appendLiteral('T')
        // Accepts strings with/without an offset, so we can use this formatter
        // for both timestamp with and without timezone
        .append(DateTimeFormatter.ISO_TIME)
        .toFormatter()

/**
 * Represents a single data coercion test case. You probably want to use [test] as a shorthand
 * constructor.
 *
 * @param name A short human-readable name for the test. Primarily useful for tests where
 * [inputValue] is either very long, or otherwise hard to read.
 * @param inputValue The value to pass into [ValueCoercer.validate]
 * @param outputValue The value that we expect to read back from the destination. Should be
 * basically equivalent to the output of [ValueCoercer.validate]
 * @param changeReason If `validate` returns Truncate/Nullify, the reason for that
 * truncation/nullification. If `validate` returns Valid, this should be null.
 */
data class DataCoercionFixture(
    val name: String,
    val inputValue: AirbyteValue,
    val outputValue: Any?,
    val changeReason: Reason? = null,
)

fun test(
    name: String,
    inputValue: AirbyteValue,
    outputValue: Any?,
    changeReason: Reason? = null,
) = DataCoercionFixture(name, inputValue, outputValue, changeReason)
