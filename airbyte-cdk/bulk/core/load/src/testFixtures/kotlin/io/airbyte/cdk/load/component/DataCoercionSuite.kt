/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.component.TableOperationsFixtures.inputRecord
import io.airbyte.cdk.load.component.TableOperationsFixtures.insertRecords
import io.airbyte.cdk.load.component.TableOperationsFixtures.removeAirbyteColumns
import io.airbyte.cdk.load.component.TableOperationsFixtures.removeNulls
import io.airbyte.cdk.load.component.TableOperationsFixtures.reverseColumnNameMapping
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.EnrichedAirbyteValue
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.NumberType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.dataflow.transform.ValidationResult
import io.airbyte.cdk.load.dataflow.transform.ValueCoercer
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange.Reason
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals

/**
 * The tests in this class are designed to reference the parameters defined in
 * `DataCoercionFixtures.kt`. For example, you might annotate [`handle integer values`] with
 * `@MethodSource("io.airbyte.cdk.load.component.DataCoercionIntegerFixtures#int32")`. See each
 * fixture class for explanations of what behavior they are exercising.
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

    /** Fixtures are defined in [DataCoercionIntegerFixtures]. */
    fun `handle integer values`(
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?
    ) = runTest {
        testValueCoercion(
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
        testValueCoercion(
            columnNameMapping,
            FieldType(NumberType, nullable = true),
            inputValue,
            expectedValue,
            expectedChangeReason,
        )
    }

    /** Apply the coercer to a value and verify that we can write the coerced value correctly */
    suspend fun testValueCoercion(
        columnNameMapping: ColumnNameMapping,
        fieldType: FieldType,
        inputValue: AirbyteValue,
        expectedValue: Any?,
        expectedChangeReason: Reason?,
    ) {
        val testNamespace = TableOperationsFixtures.generateTestNamespace("test")
        val tableName =
            TableOperationsFixtures.generateTestTableName("table-test-table", testNamespace)
        val schema = ObjectType(linkedMapOf("test" to fieldType))
        val stream =
            TableOperationsFixtures.createAppendStream(
                tableName.namespace,
                tableName.name,
                schema,
            )

        val mappedValue =
            coercer.map(
                EnrichedAirbyteValue(
                    inputValue,
                    fieldType.type,
                    "test",
                    airbyteMetaField = null,
                )
            )
        val validatedValue = coercer.validate(mappedValue)
        val valueToInsert: AirbyteValue
        val changeReason: Reason?
        when (validatedValue) {
            is ValidationResult.ShouldNullify -> {
                valueToInsert = NullValue
                changeReason = validatedValue.reason
            }
            is ValidationResult.ShouldTruncate -> {
                valueToInsert = validatedValue.truncatedValue
                changeReason = validatedValue.reason
            }
            ValidationResult.Valid -> {
                valueToInsert = inputValue
                changeReason = null
            }
        }

        opsClient.createNamespace(testNamespace)
        opsClient.createTable(stream, tableName, columnNameMapping, replace = false)
        testClient.insertRecords(
            tableName,
            columnNameMapping,
            inputRecord("test" to valueToInsert),
        )

        val actualRecords =
            testClient
                .readTable(tableName)
                .removeAirbyteColumns(airbyteMetaColumnMapping)
                .reverseColumnNameMapping(columnNameMapping, airbyteMetaColumnMapping)
                .removeNulls()
        assertEquals(
            listOf(mapOf("test" to expectedValue)).removeNulls(),
            actualRecords,
            "For input $inputValue, expected $expectedValue. Coercer output was $validatedValue.",
        )
        assertEquals(expectedChangeReason, changeReason)
    }
}
