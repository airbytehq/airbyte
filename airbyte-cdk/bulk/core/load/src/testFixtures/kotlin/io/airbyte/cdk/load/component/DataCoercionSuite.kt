/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ArrayType
import io.airbyte.cdk.load.data.ArrayTypeWithoutSchema
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.BooleanValue
import io.airbyte.cdk.load.data.DateType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.data.UnionType
import io.airbyte.cdk.load.data.UnknownType
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.TableSchemaFactory
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlinx.coroutines.test.runTest

/**
 * The tests in this class are designed to reference the parameters defined in
 * `DataCoercionFixtures.kt`. For example, you might annotate [`handle integer values`] with
 * `@MethodSource("io.airbyte.cdk.load.component.DataCoercionIntegerFixtures#int32")`. See each
 * fixture class for explanations of what behavior they are exercising.
 *
 * Note that this class _only_ exercises [ValueCoercer.validate]. You should write separate unit
 * tests for [ValueCoercer.map]. For now, the `map` function is primarily intended for transforming
 * `UnionType` fields into other types (typically `StringType`), at which point your `validate`
 * implementation should be able to handle any StringValue (regardless of whether it was originally
 * a StringType or UnionType).
 */
@MicronautTest(environments = ["component"], resolveParameters = false)
interface DataCoercionSuite {
    val coercer: ValueCoercer
    val airbyteMetaColumnMapping: Map<String, String>
        get() = Meta.COLUMN_NAMES.associateWith { it }
    val columnNameMapping: ColumnNameMapping
        get() = ColumnNameMapping(mapOf("test" to "test"))

    val opsClient: TableOperationsClient
    val testClient: TestTableOperationsClient
    val schemaFactory: TableSchemaFactory

    val harness: TableOperationsTestHarness
        get() =
            TableOperationsTestHarness(
                opsClient,
                testClient,
                schemaFactory,
                airbyteMetaColumnMapping
            )

    /** Fixtures are defined in [DataCoercionIntegerFixtures]. */
    fun `handle integer values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(IntegerType, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionNumberFixtures]. */
    fun `handle number values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(NumberType, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionTimestampTzFixtures]. */
    fun `handle timestamptz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(TimestampTypeWithTimezone, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionTimestampNtzFixtures]. */
    fun `handle timestampntz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(TimestampTypeWithoutTimezone, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionTimeTzFixtures]. */
    fun `handle timetz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(TimeTypeWithTimezone, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionTimeNtzFixtures]. */
    fun `handle timentz values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(TimeTypeWithoutTimezone, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionDateFixtures]. */
    fun `handle date values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(DateType, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** No fixtures, hardcoded to just write `true` */
    fun `handle bool values`(expectedValue: Any?) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(BooleanType, nullable = true),
            // Just test on `true` and assume `false` also works
            BooleanValue(true),
            expectedValue,
            // If your destination is nulling/truncating booleans... that's almost definitely a bug
            expectedChangeReason = null,
        )
    }

    /** Fixtures are defined in [DataCoercionStringFixtures]. */
    fun `handle string values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(StringType, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionObjectFixtures]. */
    fun `handle object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(
                ObjectType(linkedMapOf("foo" to FieldType(StringType, true))),
                nullable = true
            ),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionObjectFixtures]. */
    fun `handle empty object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(ObjectTypeWithEmptySchema, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionObjectFixtures]. */
    fun `handle schemaless object values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(ObjectTypeWithoutSchema, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionArrayFixtures]. */
    fun `handle array values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(ArrayType(FieldType(StringType, true)), nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Fixtures are defined in [DataCoercionArrayFixtures]. */
    fun `handle schemaless array values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(ArrayTypeWithoutSchema, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /**
     * All destinations should implement this, even if your destination is supporting legacy unions.
     *
     * Fixtures are defined in [DataCoercionUnionFixtures].
     */
    fun `handle union values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(
                UnionType(
                    setOf(
                        ObjectType(linkedMapOf("foo" to FieldType(StringType, true))),
                        IntegerType,
                        StringType,
                    ),
                    isLegacyUnion = false
                ),
                nullable = true
            ),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /**
     * Only legacy destinations that are maintaining "legacy" union behavior should implement this
     * test. If you're not sure, check whether your `application-connector.yaml` includes a
     * `airbyte.destination.core.types.unions: LEGACY` property.
     *
     * Fixtures are defined in [DataCoercionLegacyUnionFixtures].
     */
    fun `handle legacy union values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(
                UnionType(
                    setOf(
                        ObjectType(linkedMapOf("foo" to FieldType(StringType, true))),
                        IntegerType,
                        StringType,
                    ),
                    isLegacyUnion = true
                ),
                nullable = true
            ),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    fun `handle unknown values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        harness.testValueCoercion(
            coercer,
            columnNameMapping,
            FieldType(UnknownType(Jsons.readTree(("""{"type": "potato"}"""))), nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }
}
