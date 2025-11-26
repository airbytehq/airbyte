/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.NumberValue
import java.math.BigDecimal
import java.math.BigInteger
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
            IntegerValue(0) to 0L,
            IntegerValue(1) to 1L,
            IntegerValue(-1) to -1L,
            IntegerValue(42) to 42L,
            IntegerValue(-42) to -42L,
            // int32 bounds, and slightly out of bounds
            IntegerValue(Integer.MAX_VALUE.toLong()) to Integer.MAX_VALUE.toLong(),
            IntegerValue(Integer.MIN_VALUE.toLong()) to Integer.MIN_VALUE.toLong(),
            IntegerValue(Integer.MAX_VALUE.toLong() + 1) to Integer.MAX_VALUE.toLong() + 1,
            IntegerValue(Integer.MIN_VALUE.toLong() - 1) to Integer.MIN_VALUE.toLong() - 1,
            // int64 bounds, and slightly out of bounds
            IntegerValue(Long.MAX_VALUE) to Long.MAX_VALUE,
            IntegerValue(Long.MIN_VALUE) to Long.MIN_VALUE,
            // values out of int64 bounds are nulled
            IntegerValue(bigint(Long.MAX_VALUE) + BigInteger.ONE) to null,
            IntegerValue(bigint(Long.MIN_VALUE) - BigInteger.ONE) to null,
            // NUMERIC(38, 9) bounds, and slightly out of bounds
            // (these are all out of bounds for an int64 value, so they all get nulled)
            // TODO turn this into a struct
            //   DataCoercionTestCase(inputValue: AirbyteValue, expectedValue: Any?, changeReason:
            // Meta.Change.Reason?, description: String?)
            IntegerValue(numeric38_0Max) to null,
            IntegerValue(numeric38_0Min) to null,
            IntegerValue(numeric38_0Max + BigInteger.ONE) to null,
            IntegerValue(numeric38_0Min - BigInteger.ONE) to null,
        )

    /**
     * Many destination warehouses represent integers as a fixed-point type with 38 digits of
     * precision. In this case, we only need to null out numbers larger than `1e38 - 1` / smaller
     * than `-1e38 + 1`.
     */
    val numeric38_0 =
        listOf(
            IntegerValue(0) to bigint(0L),
            IntegerValue(1) to bigint(1L),
            IntegerValue(-1) to bigint(-1L),
            IntegerValue(42) to bigint(42L),
            IntegerValue(-42) to bigint(-42L),
            // int32 bounds, and slightly out of bounds
            IntegerValue(Integer.MAX_VALUE.toLong()) to bigint(Integer.MAX_VALUE.toLong()),
            IntegerValue(Integer.MIN_VALUE.toLong()) to bigint(Integer.MIN_VALUE.toLong()),
            IntegerValue(Integer.MAX_VALUE.toLong() + 1) to bigint(Integer.MAX_VALUE.toLong() + 1),
            IntegerValue(Integer.MIN_VALUE.toLong() - 1) to bigint(Integer.MIN_VALUE.toLong() - 1),
            // int64 bounds, and slightly out of bounds
            IntegerValue(Long.MAX_VALUE) to bigint(Long.MAX_VALUE),
            IntegerValue(Long.MIN_VALUE) to bigint(Long.MIN_VALUE),
            IntegerValue(bigint(Long.MAX_VALUE) + BigInteger.ONE) to
                bigint(Long.MAX_VALUE) + BigInteger.ONE,
            IntegerValue(bigint(Long.MIN_VALUE) - BigInteger.ONE) to
                bigint(Long.MIN_VALUE) - BigInteger.ONE,
            // NUMERIC(38, 9) bounds, and slightly out of bounds
            IntegerValue(numeric38_0Max) to numeric38_0Max,
            IntegerValue(numeric38_0Min) to numeric38_0Min,
            // These values exceed the 38-digit range, so they get nulled out
            IntegerValue(numeric38_0Max + BigInteger.ONE) to null,
            IntegerValue(numeric38_0Min - BigInteger.ONE) to null,
        )

    @JvmStatic fun int64() = int64.toArgs()

    /**
     * Convenience fixture if your [TestTableOperationsClient] returns integers as [BigInteger]
     * rather than [Long].
     */
    @JvmStatic
    fun int64AsBigInteger() = int64.map { (input, output) -> input to output?.let { bigint(it) } }

    /**
     * Convenience fixture if your [TestTableOperationsClient] returns integers as [BigDecimal]
     * rather than [Long].
     */
    @JvmStatic
    fun int64AsBigDecimal() =
        int64.map { (input, output) -> input to output?.let { BigDecimal.valueOf(it) } }

    @JvmStatic fun numeric38_0() = numeric38_0.toArgs()
}

object DataCoercionNumberFixtures {
    val numeric38_9Max = bigdec("99999999999999999999999999999.999999999")
    val numeric38_9Min = bigdec("-99999999999999999999999999999.999999999")

    val float64 =
        listOf(
            NumberValue(bigdec(0)) to 0.0,
            NumberValue(bigdec(1)) to 1.0,
            NumberValue(bigdec(-1)) to -1.0,
            // This value isn't exactly representable as a float64
            // (the exact value is `123.400000000000005684341886080801486968994140625`)
            // but we should preserve the canonical representation
            NumberValue(bigdec("123.4")) to 123.4,
            NumberValue(bigdec("-123.4")) to -123.4,
            // These values have too much precision for a float64, so we round them
            // TODO snowflake rounds these differently than expected, figure out why. Or make it
            // easier
            //   for snowflake to override specific entries in this list.
            NumberValue(bigdec("1234567890.1234567890123456789")) to 1234567890.1234567,
            NumberValue(bigdec("-1234567890.1234567890123456789")) to -1234567890.1234567,
            NumberValue(numeric38_9Max) to 1.0E29,
            NumberValue(numeric38_9Min) to -1.0E29,
            // min/max_value are all positive values, so we need to manually test their negative
            // version
            NumberValue(bigdec(Float.MIN_VALUE.toDouble())) to Float.MIN_VALUE.toDouble(),
            NumberValue(bigdec(-Float.MIN_VALUE.toDouble())) to -Float.MIN_VALUE.toDouble(),
            NumberValue(bigdec(Float.MAX_VALUE.toDouble())) to Float.MAX_VALUE.toDouble(),
            NumberValue(bigdec(-Float.MAX_VALUE.toDouble())) to -Float.MAX_VALUE.toDouble(),
            NumberValue(bigdec(Double.MIN_VALUE)) to Double.MIN_VALUE,
            NumberValue(bigdec(-Double.MIN_VALUE)) to -Double.MIN_VALUE,
            // TODO snowflake writes this value correctly, but reads it back as infinity. Need to
            // fix SnowflakeTestOperationClient
            NumberValue(bigdec(Double.MAX_VALUE)) to Double.MAX_VALUE,
            NumberValue(bigdec(-Double.MAX_VALUE)) to -Double.MAX_VALUE,
            // These values are out of bounds, so we null them
            NumberValue(bigdec(Double.MAX_VALUE) + bigdec(Double.MIN_VALUE)) to null,
            NumberValue(bigdec(-Double.MAX_VALUE) - bigdec(Double.MIN_VALUE)) to null,
        )

    val numeric38_9 =
        listOf(
                NumberValue(bigdec(0)) to bigdec(0.0),
                NumberValue(bigdec(1)) to bigdec(1.0),
                NumberValue(bigdec(-1)) to bigdec(-1.0),
                // This value isn't exactly representable as a float64
                // (the exact value is `123.400000000000005684341886080801486968994140625`)
                // but it's perfectly fine as a numeric(38, 9)
                NumberValue(bigdec("123.4")) to bigdec("123.4"),
                NumberValue(bigdec("-123.4")) to bigdec("-123.4"),
                // These values have too much precision for a numeric(38, 9), so we round them
                NumberValue(bigdec("1234567890.1234567890123456789")) to
                    bigdec("1234567890.123456789"),
                NumberValue(bigdec("-1234567890.1234567890123456789")) to
                    bigdec("-1234567890.123456789"),
                NumberValue(bigdec(Float.MIN_VALUE.toDouble())) to bigdec(0),
                NumberValue(bigdec(-Float.MIN_VALUE.toDouble())) to bigdec(0),
                NumberValue(bigdec(Double.MIN_VALUE)) to bigdec(0),
                NumberValue(bigdec(-Double.MIN_VALUE)) to bigdec(0),
                // numeric bounds are perfectly fine
                NumberValue(numeric38_9Max) to numeric38_9Max,
                NumberValue(numeric38_9Min) to numeric38_9Min,
                // These values are out of bounds, so we null them
                NumberValue(bigdec(Float.MAX_VALUE.toDouble())) to null,
                NumberValue(bigdec(-Float.MAX_VALUE.toDouble())) to null,
                NumberValue(bigdec(Double.MAX_VALUE)) to null,
                NumberValue(bigdec(-Double.MAX_VALUE)) to null,
                NumberValue(bigdec(Double.MAX_VALUE) + bigdec(Double.MIN_VALUE)) to null,
                NumberValue(bigdec(-Double.MAX_VALUE) - bigdec(Double.MIN_VALUE)) to null,
            )
            .map { (input, output) -> input to output?.setScale(9) }

    @JvmStatic fun float64() = float64.toArgs()
    @JvmStatic fun numeric38_9() = numeric38_9.toArgs()
}

fun <T, U> List<Pair<T, U>>.toArgs(): List<Arguments> =
    this.map { Arguments.of(it.first, it.second) }.toList()

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
