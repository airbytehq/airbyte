/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift_v2.component

import io.airbyte.cdk.load.component.DataCoercionDateFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.LARGEST_NEGATIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.LARGEST_POSITIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.NEGATIVE_HIGH_PRECISION_FLOAT
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.POSITIVE_HIGH_PRECISION_FLOAT
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT32
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT64
import io.airbyte.cdk.load.component.DataCoercionStringFixtures
import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.DataCoercionTimestampNtzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimestampTzFixtures
import io.airbyte.cdk.load.component.OUT_OF_RANGE_TIMESTAMP
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.component.toArgs
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import java.math.BigDecimal
import java.time.LocalDateTime
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

@MicronautTest(environments = ["component"], resolveParameters = false)
@Execution(ExecutionMode.CONCURRENT)
class RedshiftDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : DataCoercionSuite {
    override val columnNameMapping = RedshiftComponentTestFixtures.testMapping
    // Redshift uses lowercase column names
    override val airbyteMetaColumnMapping = Meta.COLUMN_NAMES.associateWith { it }

    @ParameterizedTest
    // Redshift uses BIGINT (64-bit signed integer)
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionIntegerFixtures#int64")
    override fun `handle integer values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle integer values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        // TODO switch this to use the fixed-point 38,9 fixture
        "io.airbyte.integrations.destination.redshift_v2.component.RedshiftDataCoercionTest#numbers"
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
        "io.airbyte.integrations.destination.redshift_v2.component.RedshiftDataCoercionTest#timestampTz"
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
        "io.airbyte.integrations.destination.redshift_v2.component.RedshiftDataCoercionTest#timestampNtz"
    )
    override fun `handle timestampntz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timestampntz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionTimeTzFixtures#timetz")
    override fun `handle timetz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timetz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionTimeNtzFixtures#timentz")
    override fun `handle timentz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle timentz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.redshift_v2.component.RedshiftDataCoercionTest#date"
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
        "io.airbyte.integrations.destination.redshift_v2.component.RedshiftDataCoercionTest#string"
    )
    override fun `handle string values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle string values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    // Redshift uses SUPER type for JSON/objects
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
    // Redshift uses SUPER type for arrays
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
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionUnionFixtures#unions")
    override fun `handle union values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle union values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionUnknownFixtures#unknowns")
    override fun `handle unknown values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) {
        super.`handle unknown values`(inputValue, expectedValue, expectedChangeReason)
    }

    companion object {
        @JvmStatic
        fun numbers() =
            // Redshift uses DOUBLE PRECISION which is IEEE 754 double (float64)
            DataCoercionNumberFixtures.float64
                .map {
                    when (it.name) {
                        // Redshift handles double precision similarly to Snowflake
                        // It may round floats in certain ways
                        LARGEST_POSITIVE_FLOAT64 ->
                            it.copy(
                                outputValue = BigDecimal.valueOf(Double.MAX_VALUE),
                                changeReason = null
                            )
                        LARGEST_NEGATIVE_FLOAT64 ->
                            it.copy(
                                outputValue = BigDecimal.valueOf(-Double.MAX_VALUE),
                                changeReason = null
                            )
                        POSITIVE_HIGH_PRECISION_FLOAT ->
                            it.copy(
                                outputValue = BigDecimal("1234567890.123457"),
                                changeReason = null
                            )
                        NEGATIVE_HIGH_PRECISION_FLOAT ->
                            it.copy(
                                outputValue = BigDecimal("-1234567890.123457"),
                                changeReason = null
                            )
                        SMALLEST_POSITIVE_FLOAT32 ->
                            it.copy(
                                outputValue = BigDecimal.valueOf(1.401298464324817E-45),
                                changeReason = null
                            )
                        SMALLEST_NEGATIVE_FLOAT32 ->
                            it.copy(
                                outputValue = BigDecimal.valueOf(-1.401298464324817E-45),
                                changeReason = null
                            )
                        SMALLEST_POSITIVE_FLOAT64 ->
                            it.copy(outputValue = BigDecimal.valueOf(4.9E-324), changeReason = null)
                        SMALLEST_NEGATIVE_FLOAT64 ->
                            it.copy(
                                outputValue = BigDecimal.valueOf(-4.9E-324),
                                changeReason = null
                            )
                        // Convert to bigdecimal + kill unnecessary decimal points
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
                // Redshift supports a wide range of timestamps
                // but we should verify if there are out-of-range issues
                .filter { it.name != OUT_OF_RANGE_TIMESTAMP }
                .toArgs()

        @JvmStatic
        fun timestampNtz() =
            DataCoercionTimestampNtzFixtures.commonWarehouse
                .filter { it.name != OUT_OF_RANGE_TIMESTAMP }
                .map { fixture ->
                    fixture.copy(
                        outputValue = fixture.outputValue?.let { LocalDateTime.parse(it as String) }
                    )
                }
                .toArgs()

        @JvmStatic
        fun date() =
            DataCoercionDateFixtures.commonWarehouse
                // Redshift DATE supports 4713 BC to 5874897 AD
                // so we shouldn't have out-of-range issues with standard test dates
                .filter { it.name != OUT_OF_RANGE_TIMESTAMP }
                .toArgs()

        @JvmStatic
        fun string() =
            DataCoercionStringFixtures.strings
                // TODO figure out the long strings thing
                .toArgs()
    }
}
