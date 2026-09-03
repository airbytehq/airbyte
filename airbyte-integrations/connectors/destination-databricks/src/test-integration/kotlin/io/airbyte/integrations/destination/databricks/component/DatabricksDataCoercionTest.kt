/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks.component

import io.airbyte.cdk.load.component.DataCoercionDateFixtures
import io.airbyte.cdk.load.component.DataCoercionNumberFixtures
import io.airbyte.cdk.load.component.DataCoercionStringFixtures
import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.DataCoercionTimestampNtzFixtures
import io.airbyte.cdk.load.component.DataCoercionTimestampTzFixtures
import io.airbyte.cdk.load.component.HIGH_PRECISION_TIMESTAMP
import io.airbyte.cdk.load.component.MAXIMUM_TIMESTAMP
import io.airbyte.cdk.load.component.OUT_OF_RANGE_TIMESTAMP
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.component.toArgs
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.integrations.destination.databricks.component.DatabricksDataCoercionTest.Companion.timestampTz
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import java.math.BigDecimal
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

/**
 * Data coercion tests for Databricks. Verifies that each data type is correctly coerced, written,
 * and read back through the component test framework.
 */
@MicronautTest(environments = ["component"], resolveParameters = false)
@Execution(ExecutionMode.CONCURRENT)
class DatabricksDataCoercionTest(
    override val coercer: ValueCoercer,
    override val opsClient: TableOperationsClient,
    override val testClient: TestTableOperationsClient,
    override val schemaFactory: TableSchemaFactory,
) : DataCoercionSuite {

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionIntegerFixtures#int64")
    override fun `handle integer values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle integer values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.databricks.component.DatabricksDataCoercionTest#numbers"
    )
    override fun `handle number values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle number values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.databricks.component.DatabricksDataCoercionTest#timestampTz"
    )
    override fun `handle timestamptz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timestamptz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.databricks.component.DatabricksDataCoercionTest#timestampNtz"
    )
    override fun `handle timestampntz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timestampntz values`(inputValue, expectedValue, expectedChangeReason)
    }

    override fun `handle timetz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timetz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionTimeNtzFixtures#timentz")
    override fun `handle timentz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timentz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.databricks.component.DatabricksDataCoercionTest#date"
    )
    override fun `handle date values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle date values`(inputValue, expectedValue, expectedChangeReason)
    }

    @Test
    fun `handle boolean values`() {
        super.`handle bool values`(expectedValue = true)
    }

    @ParameterizedTest
    @MethodSource(
        "io.airbyte.integrations.destination.databricks.component.DatabricksDataCoercionTest#strings"
    )
    override fun `handle string values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle string values`(inputValue, expectedValue, expectedChangeReason)
    }

    // Databricks stores objects/arrays as STRING (JSON), so use stringified fixtures
    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#stringifiedObjects")
    override fun `handle object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#stringifiedObjects")
    override fun `handle empty object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle empty object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionObjectFixtures#stringifiedObjects")
    override fun `handle schemaless object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle schemaless object values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionArrayFixtures#stringifiedArrays")
    override fun `handle array values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle array values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionArrayFixtures#stringifiedArrays")
    override fun `handle schemaless array values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle schemaless array values`(inputValue, expectedValue, expectedChangeReason)
    }

    /** Unions are serialized to JSON strings by [DatabricksValueCoercer.map] for STRING storage. */
    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionUnionFixtures#stringifiedUnions")
    override fun `handle union values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle union values`(inputValue, expectedValue, expectedChangeReason)
    }

    /** Unknown types map to STRING in Databricks. */
    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionUnknownFixtures#stringifiedUnknowns")
    override fun `handle unknown values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle unknown values`(inputValue, expectedValue, expectedChangeReason)
    }

    companion object {
        /**
         * Databricks uses DECIMAL(38, 10) for numbers, but the CDK fixture `numeric38_9` applies
         * `.setScale(9)`. We rescale to 10.
         *
         * Smallest float32/float64 values (e.g. 1.4E-45, 4.9E-324) are filtered because their
         * BigDecimal representation exceeds DECIMAL(38,10)'s total precision
         *
         * High-precision float values are in range but have excess fractional digits — the coercer
         * only validates range, not precision, so changeReason is null.
         */
        @JvmStatic
        fun numbers() =
            DataCoercionNumberFixtures.numeric38_9
                .filter {
                    it.name !in
                        setOf(
                            DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT32,
                            DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT32,
                            DataCoercionNumberFixtures.SMALLEST_POSITIVE_FLOAT64,
                            DataCoercionNumberFixtures.SMALLEST_NEGATIVE_FLOAT64,
                        )
                }
                .map { fixture ->
                    val scaled =
                        fixture.copy(
                            outputValue = (fixture.outputValue as BigDecimal?)?.setScale(10)
                        )
                    when (fixture.name) {
                        DataCoercionNumberFixtures.POSITIVE_HIGH_PRECISION_FLOAT,
                        DataCoercionNumberFixtures.NEGATIVE_HIGH_PRECISION_FLOAT ->
                            scaled.copy(changeReason = null)
                        // NUMERIC_38_9 max/min have 29 integer digits, but DECIMAL(38,10)
                        // only supports 28. The coercer correctly nullifies them.
                        DataCoercionNumberFixtures.NUMERIC_38_9_MAX,
                        DataCoercionNumberFixtures.NUMERIC_38_9_MIN ->
                            fixture.copy(
                                outputValue = null,
                                changeReason = Reason.DESTINATION_FIELD_SIZE_LIMITATION,
                            )
                        else -> scaled
                    }
                }
                .toArgs()

        /**
         * Databricks STRING has no inherent size limit, but the JDBC Thrift parameter limit (1MB)
         * prevents inserting the 16MB+ LONG_STRING test value via parameterized queries.
         */
        @JvmStatic
        fun strings() =
            DataCoercionStringFixtures.strings
                .filter { it.name != DataCoercionStringFixtures.LONG_STRING }
                .toArgs()

        /** The coercer does not validate date ranges, so year 10000+ passes through as Valid */
        @JvmStatic
        fun date() =
            DataCoercionDateFixtures.commonWarehouse
                .map { fixture ->
                    when (fixture.name) {
                        OUT_OF_RANGE_TIMESTAMP ->
                            fixture.copy(outputValue = "0001-01-01", changeReason = null)
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * Databricks TIMESTAMP has microsecond precision (6 digits) and truncates (not rounds).
         * - HIGH_PRECISION: .123456789 truncates to .123456
         * - MAXIMUM: .999999999 truncates to .999999
         * - OUT_OF_RANGE: Databricks supports a wider range including this value
         */
        @JvmStatic
        fun timestampTz() =
            DataCoercionTimestampTzFixtures.commonWarehouse
                .map { fixture ->
                    when (fixture.name) {
                        HIGH_PRECISION_TIMESTAMP ->
                            fixture.copy(outputValue = "2025-01-23T01:01:00.123456Z")
                        MAXIMUM_TIMESTAMP ->
                            fixture.copy(outputValue = "9999-12-31T23:59:59.999999Z")
                        OUT_OF_RANGE_TIMESTAMP ->
                            fixture.copy(
                                outputValue = "+10000-01-01T00:00:00Z",
                                changeReason = null,
                            )
                        else -> fixture
                    }
                }
                .toArgs()

        /**
         * Same as [timestampTz] but for timestamp without timezone. The Databricks JDBC driver
         * reports TIMESTAMP_NTZ columns as "TIMESTAMP", so [readColumn] reads them as UTC
         * OffsetDateTime strings (with Z suffix). All non-null outputs need Z appended.
         */
        @JvmStatic
        fun timestampNtz() =
            DataCoercionTimestampNtzFixtures.commonWarehouse
                .map { fixture ->
                    when (fixture.name) {
                        HIGH_PRECISION_TIMESTAMP ->
                            fixture.copy(outputValue = "2025-01-23T01:01:00.123456Z")
                        MAXIMUM_TIMESTAMP ->
                            fixture.copy(outputValue = "9999-12-31T23:59:59.999999Z")
                        OUT_OF_RANGE_TIMESTAMP ->
                            fixture.copy(
                                outputValue = "+10000-01-01T00:00:00Z",
                                changeReason = null,
                            )
                        else ->
                            fixture.let { f ->
                                val output = f.outputValue
                                if (output is String) f.copy(outputValue = "${output}Z") else f
                            }
                    }
                }
                .toArgs()
    }
}
