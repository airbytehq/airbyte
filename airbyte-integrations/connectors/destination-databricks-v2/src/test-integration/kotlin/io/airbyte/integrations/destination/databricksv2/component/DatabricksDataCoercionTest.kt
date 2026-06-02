/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricksv2.component

import io.airbyte.cdk.load.component.DataCoercionSuite
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.component.TestTableOperationsClient
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.MethodSource

/**
 * Data coercion tests for Databricks. Verifies that each data type is correctly coerced, written,
 * and read back through the component test framework.
 *
 * Databricks stores objects, arrays, unions, and unknown types as STRING (JSON), not as a native
 * structured type like Redshift's SUPER.
 */
@MicronautTest(environments = ["component"], resolveParameters = false)
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
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionNumberFixtures#numeric38_9")
    override fun `handle number values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle number values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionTimestampTzFixtures#commonWarehouse")
    override fun `handle timestamptz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timestamptz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionTimestampNtzFixtures#commonWarehouse")
    override fun `handle timestampntz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        super.`handle timestampntz values`(inputValue, expectedValue, expectedChangeReason)
    }

    @ParameterizedTest
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionTimeTzFixtures#timetz")
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
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionDateFixtures#commonWarehouse")
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
    @MethodSource("io.airbyte.cdk.load.component.DataCoercionStringFixtures#strings")
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
}
