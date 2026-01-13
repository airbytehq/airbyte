/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.component

import io.airbyte.cdk.load.component.DataCoercionDateFixtures
import io.airbyte.cdk.load.component.DataCoercionIntegerFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.LARGEST_NEGATIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.LARGEST_NEGATIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.LARGEST_POSITIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.LARGEST_POSITIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.NEGATIVE_HIGH_PRECISION_FLOAT
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.NEGATIVE_ONE
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.ONE
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.POSITIVE_HIGH_PRECISION_FLOAT
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SLIGHTLY_ABOVE_LARGEST_POSITIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SLIGHTLY_BELOW_LARGEST_NEGATIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.ZERO
import io.airbyte.cdk.load.component.DataCoercionStringFixtures
import io.airbyte.cdk.load.component.DataCoercionStringFixtures.LONG_STRING
import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.DataCoercionTimeNtzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimeTzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimestampNtzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimestampTzFixtures
import io.airbyte.cdk.load.component.DataCoercionUnionFixtures
import io.airbyte.cdk.load.component.DataCoercionUnknownFixtures
import io.airbyte.cdk.load.component.HIGH_NOON
import io.airbyte.cdk.load.component.HIGH_PRECISION_TIMESTAMP
import io.airbyte.cdk.load.component.MAX_TIME
import io.airbyte.cdk.load.component.MAXIMUM_TIMESTAMP
import io.airbyte.cdk.load.component.MIDNIGHT
import io.airbyte.cdk.load.component.OUT_OF_RANGE_TIMESTAMP
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.component.bigdec
import io.airbyte.cdk.load.component.toArgs
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import java.math.BigDecimal
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

@MicronautTest(environments = ["component"], resolveParameters = false)
@Execution(ExecutionMode.CONCURRENT)
class PostgresDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : DataCoercionSuite {
    override val columnNameMapping = PostgresComponentTestFixtures.testMapping
    override val airbyteMetaColumnMapping = PostgresComponentTestFixtures.airbyteMetaColumnMapping

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#integers"
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
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#numbers"
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
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#timestampTz"
    )
    override fun `handle timestamptz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timestamptz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#timestampNtz"
    )
    override fun `handle timestampntz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timestampntz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#timetz"
    )
    override fun `handle timetz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timetz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#timentz"
    )
    override fun `handle timentz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timentz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#date"
    )
    override fun `handle date values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle date values`(inputValue, expectedValue, expectedChangeReason)
    }

    @Test
    fun `handle boolean values`() {
        super.`handle bool values`(expectedValue = true)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#string"
    )
    override fun `handle string values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle string values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#objects")
    override fun `handle object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#objects")
    override fun `handle empty object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle empty object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#objects")
    override fun `handle schemaless object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle schemaless object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionArrayFixtures#arrays")
    override fun `handle array values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle array values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionArrayFixtures#arrays")
    override fun `handle schemaless array values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle schemaless array values`(inputValue, expectedValue, expectedChangeReason)
    }

    /**
     * We don't have special handling for legacy unions, so don't bother implementing [`handle
     * legacy union values`].
     */
    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#unions"
    )
    override fun `handle union values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle union values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.postgres.component.PostgresDataCoercionTest#unknowns"
    )
    override fun `handle unknown values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle unknown values`(inputValue, expectedValue, expectedChangeReason)
    }

    companion object {
        /**
         * PostgreSQL uses BIGINT for integers, which has the same range as int64.
         * The JDBC driver returns integers as Long.
         */
        @JvmStatic
        fun integers() = DataCoercionIntegerFixtures.int64.toArgs()

        /**
         * PostgreSQL uses DECIMAL for numbers, which has effectively unlimited precision.
         * The JDBC driver returns decimals as BigDecimal.
         * PostgreSQL stores values with full precision, so we need to match the input precision.
         */
        @JvmStatic
        fun numbers() =
            DataCoercionNumberFixtures.numeric38_9
                .map { fixture ->
                    when (fixture.name) {
                        // PostgreSQL DECIMAL preserves scale for simple values
                        // The JDBC driver returns 0.0, 1.0, -1.0 with scale 1
                        ZERO -> fixture.copy(outputValue = BigDecimal("0.0"))
                        ONE -> fixture.copy(outputValue = BigDecimal("1.0"))
                        NEGATIVE_ONE -> fixture.copy(outputValue = BigDecimal("-1.0"))
                        // PostgreSQL DECIMAL stores the full precision value
                        POSITIVE_HIGH_PRECISION_FLOAT ->
                            fixture.copy(
                                outputValue =
                                    bigdec("1234567890.1234567890123456789").stripTrailingZeros(),
                                changeReason = null,
                            )
                        NEGATIVE_HIGH_PRECISION_FLOAT ->
                            fixture.copy(
                                outputValue =
                                    bigdec("-1234567890.1234567890123456789").stripTrailingZeros(),
                                changeReason = null,
                            )
                        // PostgreSQL DECIMAL can store tiny floats
                        SMALLEST_POSITIVE_FLOAT32 ->
                            fixture.copy(
                                outputValue = bigdec(Float.MIN_VALUE.toDouble()).stripTrailingZeros(),
                                changeReason = null,
                            )
                        SMALLEST_NEGATIVE_FLOAT32 ->
                            fixture.copy(
                                outputValue = bigdec(-Float.MIN_VALUE.toDouble()).stripTrailingZeros(),
                                changeReason = null,
                            )
                        SMALLEST_POSITIVE_FLOAT64 ->
                            fixture.copy(
                                outputValue = bigdec(Double.MIN_VALUE).stripTrailingZeros(),
                                changeReason = null,
                            )
                        SMALLEST_NEGATIVE_FLOAT64 ->
                            fixture.copy(
                                outputValue = bigdec(-Double.MIN_VALUE).stripTrailingZeros(),
                                changeReason = null,
                            )
                        // PostgreSQL DECIMAL can store large floats within its range
                        // JDBC returns BigDecimal in plain notation, not scientific notation
                        LARGEST_POSITIVE_FLOAT32 ->
                            fixture.copy(
                                outputValue =
                                    BigDecimal(Float.MAX_VALUE.toDouble().toBigDecimal().toPlainString()),
                                changeReason = null,
                            )
                        LARGEST_NEGATIVE_FLOAT32 ->
                            fixture.copy(
                                outputValue =
                                    BigDecimal(
                                        (-Float.MAX_VALUE.toDouble()).toBigDecimal().toPlainString()
                                    ),
                                changeReason = null,
                            )
                        LARGEST_POSITIVE_FLOAT64 ->
                            fixture.copy(
                                outputValue =
                                    BigDecimal(Double.MAX_VALUE.toBigDecimal().toPlainString()),
                                changeReason = null,
                            )
                        LARGEST_NEGATIVE_FLOAT64 ->
                            fixture.copy(
                                outputValue =
                                    BigDecimal((-Double.MAX_VALUE).toBigDecimal().toPlainString()),
                                changeReason = null,
                            )
                        SLIGHTLY_ABOVE_LARGEST_POSITIVE_FLOAT64 ->
                            fixture.copy(
                                outputValue =
                                    (bigdec(Double.MAX_VALUE) + bigdec(Double.MIN_VALUE)),
                                changeReason = null,
                            )
                        SLIGHTLY_BELOW_LARGEST_NEGATIVE_FLOAT64 ->
                            fixture.copy(
                                outputValue =
                                    (bigdec(-Double.MAX_VALUE) - bigdec(Double.MIN_VALUE)),
                                changeReason = null,
                            )
                        else ->
                            fixture.copy(
                                outputValue =
                                    (fixture.outputValue as BigDecimal?)?.stripTrailingZeros()
                            )
                    }
                }
                .toArgs()

        /**
         * PostgreSQL supports timestamps from 4713 BC to 294276 AD.
         * The standard warehouse fixtures use year 0001 as minimum and 9999 as maximum,
         * which are within PostgreSQL's range.
         * PostgreSQL supports microsecond precision (6 decimal places) and rounds nanoseconds.
         * The test client returns timestamps as ISO formatted strings.
         */
        @JvmStatic
        fun timestampTz() =
            DataCoercionTimestampTzFixtures.commonWarehouse
                // PostgreSQL's timestamp range is 4713 BC to 294276 AD
                // Year 10000 is out of range
                .filter { fixture -> fixture.name != OUT_OF_RANGE_TIMESTAMP }
                // PostgreSQL only supports microsecond precision (6 decimal places)
                // It rounds nanoseconds, so .123456789 becomes .123457 (rounded up)
                // and .999999999 rounds up to 1.000000
                .map { fixture ->
                    when (fixture.name) {
                        // .123456789 rounds up to .123457
                        HIGH_PRECISION_TIMESTAMP ->
                            fixture.copy(outputValue = "2025-01-23T01:01:00.123457Z")
                        // .999999999 rounds up, causing the seconds to roll over
                        MAXIMUM_TIMESTAMP ->
                            fixture.copy(outputValue = "+10000-01-01T00:00:00Z")
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * Similar to timestampTz but for timestamps without timezone.
         * The test client returns these as ISO formatted strings without timezone.
         */
        @JvmStatic
        fun timestampNtz() =
            DataCoercionTimestampNtzFixtures.commonWarehouse
                .filter { fixture -> fixture.name != OUT_OF_RANGE_TIMESTAMP }
                // PostgreSQL only supports microsecond precision (6 decimal places)
                // It rounds nanoseconds
                .map { fixture ->
                    when (fixture.name) {
                        // .123456789 rounds up to .123457
                        HIGH_PRECISION_TIMESTAMP ->
                            fixture.copy(outputValue = "2025-01-23T01:01:00.123457")
                        // .999999999 rounds up, causing the seconds to roll over
                        MAXIMUM_TIMESTAMP ->
                            fixture.copy(outputValue = "+10000-01-01T00:00:00")
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * PostgreSQL supports dates from 4713 BC to 5874897 AD.
         * The standard warehouse fixtures are within this range.
         * The JDBC driver returns dates as java.sql.Date which maps to LocalDate.
         */
        @JvmStatic
        fun date() =
            DataCoercionDateFixtures.commonWarehouse
                .filter { fixture -> fixture.name != OUT_OF_RANGE_TIMESTAMP }
                .map { fixture ->
                    fixture.copy(
                        outputValue =
                            fixture.outputValue?.let { value ->
                                java.sql.Date.valueOf(java.time.LocalDate.parse(value as String))
                            }
                    )
                }
                .toArgs()

        /**
         * PostgreSQL TEXT has a limit of 1GB.
         * The LONG_STRING fixture (16MB + 1 byte) is well within this limit.
         */
        @JvmStatic
        fun string() =
            DataCoercionStringFixtures.strings
                .map { fixture ->
                    when (fixture.name) {
                        // PostgreSQL can handle up to 1GB strings, so the 16MB test string is fine
                        LONG_STRING ->
                            fixture.copy(
                                outputValue = (fixture.inputValue as StringValue).value,
                                changeReason = null,
                            )
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * PostgreSQL stores unions as JSONB (via VARCHAR after serialization by the coercer).
         * The PostgresValueCoercer serializes union values to strings.
         */
        @JvmStatic
        fun unions() = DataCoercionUnionFixtures.stringifiedUnions.toArgs()

        /**
         * PostgreSQL stores unknown types as JSONB (via VARCHAR after serialization by the coercer).
         * The PostgresValueCoercer serializes unknown values to strings.
         */
        @JvmStatic
        fun unknowns() = DataCoercionUnknownFixtures.stringifiedUnknowns.toArgs()

        /**
         * PostgreSQL TIME WITH TIME ZONE - the coercer passes values through unchanged.
         * The test client returns times as ISO formatted strings with seconds.
         * Note: MAX_TIME is filtered out because PostgreSQL's timetz behavior with
         * high-precision nanoseconds and timezone conversion is timezone-dependent.
         */
        @JvmStatic
        fun timetz() =
            DataCoercionTimeTzFixtures.timetz
                // Filter out MAX_TIME because PostgreSQL's timetz behavior with
                // high-precision nanoseconds is timezone-dependent
                .filter { fixture -> fixture.name != MAX_TIME }
                .map { fixture ->
                    when (fixture.name) {
                        // Values are passed through unchanged by the coercer
                        // The test client formats times with full seconds precision
                        MIDNIGHT -> fixture.copy(outputValue = "00:00:00Z")
                        HIGH_NOON -> fixture.copy(outputValue = "12:00:00Z")
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * PostgreSQL TIME WITHOUT TIME ZONE - the coercer passes values through unchanged.
         * The test client returns times as ISO formatted strings with seconds.
         */
        @JvmStatic
        fun timentz() =
            DataCoercionTimeNtzFixtures.timentz
                .map { fixture ->
                    when (fixture.name) {
                        // Values are passed through unchanged by the coercer
                        // The test client formats times with full seconds precision
                        MAX_TIME -> fixture.copy(outputValue = "23:59:59.999999999")
                        MIDNIGHT -> fixture.copy(outputValue = "00:00:00")
                        HIGH_NOON -> fixture.copy(outputValue = "12:00:00")
                        else -> fixture
                    }
                }
                .toArgs()
    }
}
