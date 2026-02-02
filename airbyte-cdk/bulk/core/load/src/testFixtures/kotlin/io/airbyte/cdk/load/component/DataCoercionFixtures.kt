/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayValue
import io.airbyte.cdk.load.data.DateValue
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimeWithTimezoneValue
import io.airbyte.cdk.load.data.TimeWithoutTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.data.TimestampWithoutTimezoneValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.util.serializeToString
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

    const val ZERO = "0"
    const val ONE = "1"
    const val NEGATIVE_ONE = "-1"
    const val FORTY_TWO = "42"
    const val NEGATIVE_FORTY_TWO = "-42"
    const val INT32_MAX = "int32 max"
    const val INT32_MIN = "int32 min"
    const val INT32_MAX_PLUS_ONE = "int32_max + 1"
    const val INT32_MIN_MINUS_ONE = "int32_min - 1"
    const val INT64_MAX = "int64 max"
    const val INT64_MIN = "int64 min"
    const val INT64_MAX_PLUS_ONE = "int64_max + 1"
    const val INT64_MIN_MINUS_1 = "int64_min - 1"
    const val NUMERIC_38_0_MAX = "numeric(38,0) max"
    const val NUMERIC_38_0_MIN = "numeric(38,0) min"
    const val NUMERIC_38_0_MAX_PLUS_ONE = "numeric(38,0)_max + 1"
    const val NUMERIC_38_0_MIN_MINUS_ONE = "numeric(38,0)_min - 1"

    /**
     * Many destinations use int64 to represent integers. In this case, we null out any value beyond
     * Long.MIN/MAX_VALUE.
     */
    val int64 =
        listOf(
            case(NULL, NullValue, null),
            case(ZERO, IntegerValue(0), 0L),
            case(ONE, IntegerValue(1), 1L),
            case(NEGATIVE_ONE, IntegerValue(-1), -1L),
            case(FORTY_TWO, IntegerValue(42), 42L),
            case(NEGATIVE_FORTY_TWO, IntegerValue(-42), -42L),
            // int32 bounds, and slightly out of bounds
            case(INT32_MAX, IntegerValue(Integer.MAX_VALUE.toLong()), Integer.MAX_VALUE.toLong()),
            case(INT32_MIN, IntegerValue(Integer.MIN_VALUE.toLong()), Integer.MIN_VALUE.toLong()),
            case(
                INT32_MAX_PLUS_ONE,
                IntegerValue(Integer.MAX_VALUE.toLong() + 1),
                Integer.MAX_VALUE.toLong() + 1
            ),
            case(
                INT32_MIN_MINUS_ONE,
                IntegerValue(Integer.MIN_VALUE.toLong() - 1),
                Integer.MIN_VALUE.toLong() - 1
            ),
            // int64 bounds, and slightly out of bounds
            case(INT64_MAX, IntegerValue(Long.MAX_VALUE), Long.MAX_VALUE),
            case(INT64_MIN, IntegerValue(Long.MIN_VALUE), Long.MIN_VALUE),
            // values out of int64 bounds are nulled
            case(
                INT64_MAX_PLUS_ONE,
                IntegerValue(bigint(Long.MAX_VALUE) + BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                INT64_MIN_MINUS_1,
                IntegerValue(bigint(Long.MIN_VALUE) - BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            // NUMERIC(38, 9) bounds, and slightly out of bounds
            // (these are all out of bounds for an int64 value, so they all get nulled)
            case(
                NUMERIC_38_0_MAX,
                IntegerValue(numeric38_0Max),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                NUMERIC_38_0_MIN,
                IntegerValue(numeric38_0Min),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                NUMERIC_38_0_MAX_PLUS_ONE,
                IntegerValue(numeric38_0Max + BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                NUMERIC_38_0_MIN_MINUS_ONE,
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
            case(NULL, NullValue, null),
            case(ZERO, IntegerValue(0), bigint(0L)),
            case(ONE, IntegerValue(1), bigint(1L)),
            case(NEGATIVE_ONE, IntegerValue(-1), bigint(-1L)),
            case(FORTY_TWO, IntegerValue(42), bigint(42L)),
            case(NEGATIVE_FORTY_TWO, IntegerValue(-42), bigint(-42L)),
            // int32 bounds, and slightly out of bounds
            case(
                INT32_MAX,
                IntegerValue(Integer.MAX_VALUE.toLong()),
                bigint(Integer.MAX_VALUE.toLong())
            ),
            case(
                INT32_MIN,
                IntegerValue(Integer.MIN_VALUE.toLong()),
                bigint(Integer.MIN_VALUE.toLong())
            ),
            case(
                INT32_MAX_PLUS_ONE,
                IntegerValue(Integer.MAX_VALUE.toLong() + 1),
                bigint(Integer.MAX_VALUE.toLong() + 1)
            ),
            case(
                INT32_MIN_MINUS_ONE,
                IntegerValue(Integer.MIN_VALUE.toLong() - 1),
                bigint(Integer.MIN_VALUE.toLong() - 1)
            ),
            // int64 bounds, and slightly out of bounds
            case(INT64_MAX, IntegerValue(Long.MAX_VALUE), bigint(Long.MAX_VALUE)),
            case(INT64_MIN, IntegerValue(Long.MIN_VALUE), bigint(Long.MIN_VALUE)),
            case(
                INT64_MAX_PLUS_ONE,
                IntegerValue(bigint(Long.MAX_VALUE) + BigInteger.ONE),
                bigint(Long.MAX_VALUE) + BigInteger.ONE
            ),
            case(
                INT64_MIN_MINUS_1,
                IntegerValue(bigint(Long.MIN_VALUE) - BigInteger.ONE),
                bigint(Long.MIN_VALUE) - BigInteger.ONE
            ),
            // NUMERIC(38, 9) bounds, and slightly out of bounds
            case(NUMERIC_38_0_MAX, IntegerValue(numeric38_0Max), numeric38_0Max),
            case(NUMERIC_38_0_MIN, IntegerValue(numeric38_0Min), numeric38_0Min),
            // These values exceed the 38-digit range, so they get nulled out
            case(
                NUMERIC_38_0_MAX_PLUS_ONE,
                IntegerValue(numeric38_0Max + BigInteger.ONE),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                NUMERIC_38_0_MIN_MINUS_ONE,
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

    const val ZERO = "0"
    const val ONE = "1"
    const val NEGATIVE_ONE = "-1"
    const val ONE_HUNDRED_TWENTY_THREE_POINT_FOUR = "123.4"
    const val NEGATIVE_ONE_HUNDRED_TWENTY_THREE_POINT_FOUR = "123.4"
    const val POSITIVE_HIGH_PRECISION_FLOAT = "positive high-precision float"
    const val NEGATIVE_HIGH_PRECISION_FLOAT = "negative high-precision float"
    const val NUMERIC_38_9_MAX = "numeric(38,9) max"
    const val NUMERIC_38_9_MIN = "numeric(38,9) min"
    const val SMALLEST_POSITIVE_FLOAT32 = "smallest positive float32"
    const val SMALLEST_NEGATIVE_FLOAT32 = "smallest negative float32"
    const val LARGEST_POSITIVE_FLOAT32 = "largest positive float32"
    const val LARGEST_NEGATIVE_FLOAT32 = "largest negative float32"
    const val SMALLEST_POSITIVE_FLOAT64 = "smallest positive float64"
    const val SMALLEST_NEGATIVE_FLOAT64 = "smallest negative float64"
    const val LARGEST_POSITIVE_FLOAT64 = "largest positive float64"
    const val LARGEST_NEGATIVE_FLOAT64 = "largest negative float64"
    const val SLIGHTLY_ABOVE_LARGEST_POSITIVE_FLOAT64 = "slightly above largest positive float64"
    const val SLIGHTLY_BELOW_LARGEST_NEGATIVE_FLOAT64 = "slightly below largest negative float64"

    val float64 =
        listOf(
            case(NULL, NullValue, null),
            case(ZERO, NumberValue(bigdec(0)), 0.0),
            case(ONE, NumberValue(bigdec(1)), 1.0),
            case(NEGATIVE_ONE, NumberValue(bigdec(-1)), -1.0),
            // This value isn't exactly representable as a float64
            // (the exact value is `123.400000000000005684341886080801486968994140625`)
            // but we should preserve the canonical representation
            case(ONE_HUNDRED_TWENTY_THREE_POINT_FOUR, NumberValue(bigdec("123.4")), 123.4),
            case(
                NEGATIVE_ONE_HUNDRED_TWENTY_THREE_POINT_FOUR,
                NumberValue(bigdec("-123.4")),
                -123.4
            ),
            // These values have too much precision for a float64, so we round them
            case(
                POSITIVE_HIGH_PRECISION_FLOAT,
                NumberValue(bigdec("1234567890.1234567890123456789")),
                1234567890.1234567,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                NEGATIVE_HIGH_PRECISION_FLOAT,
                NumberValue(bigdec("-1234567890.1234567890123456789")),
                -1234567890.1234567,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                NUMERIC_38_9_MAX,
                NumberValue(numeric38_9Max),
                1.0E29,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                NUMERIC_38_9_MIN,
                NumberValue(numeric38_9Min),
                -1.0E29,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            // min/max_value are all positive values, so we need to manually test their negative
            // version
            case(
                SMALLEST_POSITIVE_FLOAT32,
                NumberValue(bigdec(Float.MIN_VALUE.toDouble())),
                Float.MIN_VALUE.toDouble()
            ),
            case(
                SMALLEST_NEGATIVE_FLOAT32,
                NumberValue(bigdec(-Float.MIN_VALUE.toDouble())),
                -Float.MIN_VALUE.toDouble()
            ),
            case(
                LARGEST_POSITIVE_FLOAT32,
                NumberValue(bigdec(Float.MAX_VALUE.toDouble())),
                Float.MAX_VALUE.toDouble()
            ),
            case(
                LARGEST_NEGATIVE_FLOAT32,
                NumberValue(bigdec(-Float.MAX_VALUE.toDouble())),
                -Float.MAX_VALUE.toDouble()
            ),
            case(
                SMALLEST_POSITIVE_FLOAT64,
                NumberValue(bigdec(Double.MIN_VALUE)),
                Double.MIN_VALUE
            ),
            case(
                SMALLEST_NEGATIVE_FLOAT64,
                NumberValue(bigdec(-Double.MIN_VALUE)),
                -Double.MIN_VALUE
            ),
            case(LARGEST_POSITIVE_FLOAT64, NumberValue(bigdec(Double.MAX_VALUE)), Double.MAX_VALUE),
            case(
                LARGEST_NEGATIVE_FLOAT64,
                NumberValue(bigdec(-Double.MAX_VALUE)),
                -Double.MAX_VALUE
            ),
            // These values are out of bounds, so we null them
            case(
                SLIGHTLY_ABOVE_LARGEST_POSITIVE_FLOAT64,
                NumberValue(bigdec(Double.MAX_VALUE) + bigdec(Double.MIN_VALUE)),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                SLIGHTLY_BELOW_LARGEST_NEGATIVE_FLOAT64,
                NumberValue(bigdec(-Double.MAX_VALUE) - bigdec(Double.MIN_VALUE)),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
        )

    val numeric38_9 =
        listOf(
                case(NULL, NullValue, null),
                case(ZERO, NumberValue(bigdec(0)), bigdec(0.0)),
                case(ONE, NumberValue(bigdec(1)), bigdec(1.0)),
                case(NEGATIVE_ONE, NumberValue(bigdec(-1)), bigdec(-1.0)),
                // This value isn't exactly representable as a float64
                // (the exact value is `123.400000000000005684341886080801486968994140625`)
                // but it's perfectly fine as a numeric(38, 9)
                case(
                    ONE_HUNDRED_TWENTY_THREE_POINT_FOUR,
                    NumberValue(bigdec("123.4")),
                    bigdec("123.4")
                ),
                case(
                    NEGATIVE_ONE_HUNDRED_TWENTY_THREE_POINT_FOUR,
                    NumberValue(bigdec("-123.4")),
                    bigdec("-123.4")
                ),
                // These values have too much precision for a numeric(38, 9), so we round them
                case(
                    POSITIVE_HIGH_PRECISION_FLOAT,
                    NumberValue(bigdec("1234567890.1234567890123456789")),
                    bigdec("1234567890.123456789"),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    NEGATIVE_HIGH_PRECISION_FLOAT,
                    NumberValue(bigdec("-1234567890.1234567890123456789")),
                    bigdec("-1234567890.123456789"),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    SMALLEST_POSITIVE_FLOAT32,
                    NumberValue(bigdec(Float.MIN_VALUE.toDouble())),
                    bigdec(0),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    SMALLEST_NEGATIVE_FLOAT32,
                    NumberValue(bigdec(-Float.MIN_VALUE.toDouble())),
                    bigdec(0),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    SMALLEST_POSITIVE_FLOAT64,
                    NumberValue(bigdec(Double.MIN_VALUE)),
                    bigdec(0),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    SMALLEST_NEGATIVE_FLOAT64,
                    NumberValue(bigdec(-Double.MIN_VALUE)),
                    bigdec(0),
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                // numeric bounds are perfectly fine
                case(NUMERIC_38_9_MAX, NumberValue(numeric38_9Max), numeric38_9Max),
                case(NUMERIC_38_9_MIN, NumberValue(numeric38_9Min), numeric38_9Min),
                // These values are out of bounds, so we null them
                case(
                    LARGEST_POSITIVE_FLOAT32,
                    NumberValue(bigdec(Float.MAX_VALUE.toDouble())),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    LARGEST_NEGATIVE_FLOAT32,
                    NumberValue(bigdec(-Float.MAX_VALUE.toDouble())),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    LARGEST_POSITIVE_FLOAT64,
                    NumberValue(bigdec(Double.MAX_VALUE)),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    LARGEST_NEGATIVE_FLOAT64,
                    NumberValue(bigdec(-Double.MAX_VALUE)),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    SLIGHTLY_ABOVE_LARGEST_POSITIVE_FLOAT64,
                    NumberValue(bigdec(Double.MAX_VALUE) + bigdec(Double.MIN_VALUE)),
                    null,
                    Reason.DESTINATION_FIELD_SIZE_LIMITATION
                ),
                case(
                    SLIGHTLY_BELOW_LARGEST_NEGATIVE_FLOAT64,
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
            case(NULL, NullValue, null),
            case(
                SIMPLE_TIMESTAMP,
                TimestampWithTimezoneValue("2025-01-23T12:34:56.789Z"),
                "2025-01-23T12:34:56.789Z",
            ),
            case(
                UNIX_EPOCH,
                TimestampWithTimezoneValue("1970-01-01T00:00:00Z"),
                "1970-01-01T00:00:00Z",
            ),
            case(
                MINIMUM_TIMESTAMP,
                TimestampWithTimezoneValue("0001-01-01T00:00:00Z"),
                "0001-01-01T00:00:00Z",
            ),
            case(
                MAXIMUM_TIMESTAMP,
                TimestampWithTimezoneValue("9999-12-31T23:59:59.999999999Z"),
                "9999-12-31T23:59:59.999999999Z",
            ),
            case(
                OUT_OF_RANGE_TIMESTAMP,
                TimestampWithTimezoneValue(odt("10000-01-01T00:00Z")),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            ),
            case(
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
            case(NULL, NullValue, null),
            case(
                SIMPLE_TIMESTAMP,
                TimestampWithoutTimezoneValue("2025-01-23T12:34:56.789"),
                "2025-01-23T12:34:56.789",
            ),
            case(
                UNIX_EPOCH,
                TimestampWithoutTimezoneValue("1970-01-01T00:00:00"),
                "1970-01-01T00:00:00",
            ),
            case(
                MINIMUM_TIMESTAMP,
                TimestampWithoutTimezoneValue("0001-01-01T00:00:00"),
                "0001-01-01T00:00:00",
            ),
            case(
                MAXIMUM_TIMESTAMP,
                TimestampWithoutTimezoneValue("9999-12-31T23:59:59.999999999"),
                "9999-12-31T23:59:59.999999999",
            ),
            case(
                OUT_OF_RANGE_TIMESTAMP,
                TimestampWithoutTimezoneValue(ldt("10000-01-01T00:00")),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            ),
            case(
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
            case(NULL, NullValue, null),
            case(MIDNIGHT, TimeWithTimezoneValue("00:00Z"), "00:00Z"),
            case(MAX_TIME, TimeWithTimezoneValue("23:59:59.999999999Z"), "23:59:59.999999999Z"),
            case(HIGH_NOON, TimeWithTimezoneValue("12:00Z"), "12:00Z"),
        )

    @JvmStatic fun timetz() = timetz.toArgs()
}

object DataCoercionTimeNtzFixtures {
    val timentz =
        listOf(
            case(NULL, NullValue, null),
            case(MIDNIGHT, TimeWithoutTimezoneValue("00:00"), "00:00"),
            case(MAX_TIME, TimeWithoutTimezoneValue("23:59:59.999999999"), "23:59:59.999999999"),
            case(HIGH_NOON, TimeWithoutTimezoneValue("12:00"), "12:00"),
        )

    @JvmStatic fun timentz() = timentz.toArgs()
}

object DataCoercionDateFixtures {
    val commonWarehouse =
        listOf(
            case(NULL, NullValue, null),
            case(
                SIMPLE_TIMESTAMP,
                DateValue("2025-01-23"),
                "2025-01-23",
            ),
            case(
                UNIX_EPOCH,
                DateValue("1970-01-01"),
                "1970-01-01",
            ),
            case(
                MINIMUM_TIMESTAMP,
                DateValue("0001-01-01"),
                "0001-01-01",
            ),
            case(
                MAXIMUM_TIMESTAMP,
                DateValue("9999-12-31"),
                "9999-12-31",
            ),
            case(
                OUT_OF_RANGE_TIMESTAMP,
                DateValue(date("10000-01-01")),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION,
            ),
        )

    @JvmStatic fun commonWarehouse() = commonWarehouse.toArgs()
}

object DataCoercionStringFixtures {
    const val EMPTY_STRING = "empty string"
    const val SHORT_STRING = "short string"
    const val LONG_STRING = "long string"
    const val SPECIAL_CHARS_STRING = "special chars string"

    val strings =
        listOf(
            case(NULL, NullValue, null),
            case(EMPTY_STRING, StringValue(""), ""),
            case(SHORT_STRING, StringValue("foo"), "foo"),
            // Implementers may override this to test their destination-specific limits.
            // The default value is 8MB + 1 byte (slightly longer than snowflake's varchar limit).
            case(
                LONG_STRING,
                StringValue("a".repeat(16777216 + 1)),
                null,
                Reason.DESTINATION_FIELD_SIZE_LIMITATION
            ),
            case(
                SPECIAL_CHARS_STRING,
                StringValue("`~!@#$%^&*()-=_+[]\\{}|o'O\",./<>?)Δ⅀↑∀"),
                "`~!@#$%^&*()-=_+[]\\{}|o'O\",./<>?)Δ⅀↑∀"
            ),
        )

    @JvmStatic fun strings() = strings.toArgs()
}

object DataCoercionObjectFixtures {
    const val EMPTY_OBJECT = "empty object"
    const val NORMAL_OBJECT = "normal object"

    val objects =
        listOf(
            case(NULL, NullValue, null),
            case(EMPTY_OBJECT, ObjectValue(linkedMapOf()), emptyMap<String, Any?>()),
            case(
                NORMAL_OBJECT,
                ObjectValue(linkedMapOf("foo" to StringValue("bar"))),
                mapOf("foo" to "bar")
            ),
        )

    val stringifiedObjects =
        objects.map { fixture ->
            fixture.copy(outputValue = fixture.outputValue?.serializeToString())
        }

    @JvmStatic fun objects() = objects.toArgs()

    @JvmStatic fun stringifiedObjects() = stringifiedObjects.toArgs()
}

object DataCoercionArrayFixtures {
    const val EMPTY_ARRAY = "empty array"
    const val NORMAL_ARRAY = "normal array"

    val arrays =
        listOf(
            case(NULL, NullValue, null),
            case(EMPTY_ARRAY, ArrayValue(emptyList()), emptyList<Any?>()),
            case(NORMAL_ARRAY, ArrayValue(listOf(StringValue("foo"))), listOf("foo")),
        )

    val stringifiedArrays =
        arrays.map { fixture ->
            fixture.copy(outputValue = fixture.outputValue?.serializeToString())
        }

    @JvmStatic fun arrays() = arrays.toArgs()

    @JvmStatic fun stringifiedArrays() = stringifiedArrays.toArgs()
}

const val UNION_INT_VALUE = "int value"
const val UNION_OBJ_VALUE = "object value"
const val UNION_STR_VALUE = "string value"

object DataCoercionUnionFixtures {
    val unions =
        listOf(
            case(NULL, NullValue, null),
            case(UNION_INT_VALUE, IntegerValue(42), 42L),
            case(UNION_STR_VALUE, StringValue("foo"), "foo"),
            case(
                UNION_OBJ_VALUE,
                ObjectValue(linkedMapOf("foo" to StringValue("bar"))),
                mapOf("foo" to "bar")
            ),
        )

    val stringifiedUnions =
        unions.map { fixture ->
            fixture.copy(outputValue = fixture.outputValue?.serializeToString())
        }

    @JvmStatic fun unions() = unions.toArgs()

    @JvmStatic fun stringifiedUnions() = stringifiedUnions.toArgs()
}

object DataCoercionLegacyUnionFixtures {
    val unions =
        listOf(
            case(NULL, NullValue, null),
            // Legacy union of int x object will select object, and you can't write an int to an
            // object column.
            // So we should null it out.
            case(UNION_INT_VALUE, IntegerValue(42), null, Reason.DESTINATION_TYPECAST_ERROR),
            // Similarly, we should null out strings.
            case(UNION_STR_VALUE, StringValue("foo"), "foo"),
            // But objects can be written as objects, so retain this value.
            case(
                UNION_OBJ_VALUE,
                ObjectValue(linkedMapOf("foo" to StringValue("bar"))),
                mapOf("foo" to "bar")
            ),
        )

    val stringifiedUnions =
        DataCoercionUnionFixtures.unions.map { fixture ->
            fixture.copy(outputValue = fixture.outputValue?.serializeToString())
        }

    @JvmStatic fun unions() = unions.toArgs()

    @JvmStatic fun stringifiedUnions() = DataCoercionUnionFixtures.stringifiedUnions.toArgs()
}

// This is pretty much identical to UnionFixtures, but separating them in case we need to add
// different test cases for either of them.
object DataCoercionUnknownFixtures {
    const val INT_VALUE = "integer value"
    const val STR_VALUE = "string value"
    const val OBJ_VALUE = "object value"

    val unknowns =
        listOf(
            case(NULL, NullValue, null),
            case(INT_VALUE, IntegerValue(42), 42L),
            case(STR_VALUE, StringValue("foo"), "foo"),
            case(
                OBJ_VALUE,
                ObjectValue(linkedMapOf("foo" to StringValue("bar"))),
                mapOf("foo" to "bar")
            ),
        )

    val stringifiedUnknowns =
        unknowns.map { fixture ->
            fixture.copy(outputValue = fixture.outputValue?.serializeToString())
        }

    @JvmStatic fun unknowns() = unknowns.toArgs()

    @JvmStatic fun stringifiedUnknowns() = stringifiedUnknowns.toArgs()
}

fun List<DataCoercionTestCase>.toArgs(): List<Arguments> =
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
 * Represents a single data coercion test case. You probably want to use [case] as a shorthand
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
data class DataCoercionTestCase(
    val name: String,
    val inputValue: AirbyteValue,
    val outputValue: Any?,
    val changeReason: Reason? = null,
)

fun case(
    name: String,
    inputValue: AirbyteValue,
    outputValue: Any?,
    changeReason: Reason? = null,
) = DataCoercionTestCase(name, inputValue, outputValue, changeReason)

const val NULL = "null"
