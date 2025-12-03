/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.component

import io.airbyte.cdk.load.component.DataCoercionIntegerFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures
import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.DataCoercionTimestampTzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimestampTzFixtures.OUT_OF_RANGE_TIMESTAMP
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.component.toArgs
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import java.math.BigDecimal
import java.math.BigInteger
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

@MicronautTest(environments = ["component"], resolveParameters = false)
@Execution(ExecutionMode.CONCURRENT)
class SnowflakeDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
) : DataCoercionSuite {
    override val columnNameMapping = SnowflakeComponentTestFixtures.testMapping
    override val airbyteMetaColumnMapping = SnowflakeComponentTestFixtures.airbyteMetaColumnMapping

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.snowflake.component.SnowflakeDataCoercionTest#integers"
    )
    override fun `handle integer values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle integer values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.snowflake.component.SnowflakeDataCoercionTest#numbers"
    )
    override fun `handle number values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle number values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.snowflake.component.SnowflakeDataCoercionTest#timestampTz"
    )
    override fun `handle timestamptz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timestamptz values`(inputValue, expectedValue, expectedChangeReason)
    }

    companion object {
        /**
         * Snowflake does two interesting things when querying a `NUMERIC(38, 0)` column:
         * 1. Most values are returned as BigDecimal, rather than BigInteger
         * 2. Values within the `Long` range are returned as Long
         *
         * Otherwise, it's a totally standard NUMERIC(38, 0) column, so we can just modify the
         * numeric38_0 fixture.
         */
        @JvmStatic
        fun integers() =
            DataCoercionIntegerFixtures.numeric38_0
                .map {
                    it.copy(
                        outputValue =
                            (it.outputValue as BigInteger?)?.let {
                                try {
                                    // try to convert to long
                                    it.longValueExact()
                                } catch (_: Exception) {
                                    // if we can't (probably because the value is too large),
                                    // convert to bigdecimal
                                    it.toBigDecimal()
                                }
                            }
                    )
                }
                .toArgs()

        @JvmStatic
        fun numbers() =
            // for historical reasons, we use snowflake's FLOAT data type, which is a float64
            DataCoercionNumberFixtures.float64
                .map {
                    when (it.name) {
                        // Snowflake rounds off floats in weird ways, most of which we don't track
                        // in the value coercer. E.g.:
                        // 1.7976931348623157e308 (Double.MAX_VALUE)
                        // 1.79769313486232e308 (value read back from Snowflake)
                        // Note that snowflake's value is rounded up, so it isn't actually
                        // representable as a java double (BigDecimal(it).toDouble() => Infinity)
                        // so we have to convert to bigdecimal.
                        "largest positive float64" ->
                            it.copy(
                                outputValue = BigDecimal("1.79769313486232e308"),
                                changeReason = null
                            )
                        "largest negative float64" ->
                            it.copy(
                                outputValue = BigDecimal("-1.79769313486232e308"),
                                changeReason = null
                            )
                        // 1234567890.1234567 -> 1234567890.12346
                        // this one preserves the DESTINATION_FIELD_SIZE_LIMITATION reason,
                        // because the coercer correctly detects that the input value has too much
                        // precision for a java double
                        "positive high-precision float" ->
                            it.copy(outputValue = BigDecimal("1234567890.12346"))
                        "negative high-precision float" ->
                            it.copy(outputValue = BigDecimal("-1234567890.12346"))
                        // 1.401298464324817E-45 -> 1.401298464E-45
                        "smallest positive float32" ->
                            it.copy(
                                outputValue = BigDecimal("1.401298464E-45"),
                                changeReason = null
                            )
                        "smallest negative float32" ->
                            it.copy(
                                outputValue = BigDecimal("-1.401298464E-45"),
                                changeReason = null
                            )
                        // 3.4028234663852886E+38 -> 3.40282346638529E+38
                        "largest positive float32" ->
                            it.copy(
                                outputValue = BigDecimal("3.40282346638529E+38"),
                                changeReason = null
                            )
                        "largest negative float32" ->
                            it.copy(
                                outputValue = BigDecimal("-3.40282346638529E+38"),
                                changeReason = null
                            )
                        // 4.9E-324 -> 4.940656458E-324
                        // (this looks like snowflake is basically doing BigDecimal(4.9e-324) rather
                        // than BigDecimal.valueOf(), but that doesn't really explain the other
                        // rounding behaviors)
                        "smallest positive float64" ->
                            it.copy(
                                outputValue = BigDecimal("4.940656458E-324"),
                                changeReason = null
                            )
                        "smallest negative float64" ->
                            it.copy(
                                outputValue = BigDecimal("-4.940656458E-324"),
                                changeReason = null
                            )
                        // convert to bigdecimal + kill unnecessary decimal points (e.g. use `1`
                        // instead of `1.0`) but otherwise leave the value unchanged
                        else ->
                            it.copy(
                                outputValue =
                                    (it.outputValue as Double?)?.let {
                                        BigDecimal.valueOf(it).stripTrailingZeros()
                                    }
                            )
                    }
                }
                .toArgs()

        @JvmStatic
        fun timestampTz() =
            DataCoercionTimestampTzFixtures.commonWarehouse
                // our ValueCoercer doesn't actually validate timestamps being in-bounds yet
                // (https://github.com/airbytehq/airbyte-internal-issues/issues/15484)
                .filter { it.name != OUT_OF_RANGE_TIMESTAMP }
                .toArgs()
    }
}
