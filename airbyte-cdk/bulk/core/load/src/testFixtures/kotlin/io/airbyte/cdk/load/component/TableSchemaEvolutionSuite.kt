/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.component.TableOperationsFixtures as Fixtures
import io.airbyte.cdk.load.component.TableOperationsFixtures.ID_FIELD
import io.airbyte.cdk.load.component.TableOperationsFixtures.TEST_FIELD
import io.airbyte.cdk.load.component.TableOperationsFixtures.insertRecords
import io.airbyte.cdk.load.component.TableOperationsFixtures.removeNulls
import io.airbyte.cdk.load.component.TableOperationsFixtures.reverseColumnNameMapping
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.TimestampWithTimezoneValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_EXTRACTED_AT
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_GENERATION_ID
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_META
import io.airbyte.cdk.load.message.Meta.Companion.COLUMN_NAME_AB_RAW_ID
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.assertAll

@MicronautTest(environments = ["component"])
interface TableSchemaEvolutionSuite {
    val client: TableSchemaEvolutionClient
    val airbyteMetaColumnMapping: Map<String, String>
        get() = Meta.COLUMN_NAMES.associateWith { it }

    val opsClient: TableOperationsClient
    val testClient: TestTableOperationsClient

    private val harness: TableOperationsTestHarness
        get() = TableOperationsTestHarness(opsClient, testClient, airbyteMetaColumnMapping)

    /**
     * Test that the connector can correctly discover all of its own data types. This test creates a
     * table with a column for each data type, then tries to discover its schema.
     *
     * @param expectedDiscoveredSchema The schema to expect. This should be the same schema as
     * [computeSchema].
     */
    fun discover(expectedDiscoveredSchema: TableSchema) {
        discover(expectedDiscoveredSchema, Fixtures.ALL_TYPES_MAPPING)
    }

    fun discover(expectedDiscoveredSchema: TableSchema, columnNameMapping: ColumnNameMapping) =
        runTest {
            val testNamespace = Fixtures.generateTestNamespace("namespace-test")
            val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
            val stream =
                Fixtures.createAppendStream(
                    namespace = testTable.namespace,
                    name = testTable.name,
                    schema = Fixtures.ALL_TYPES_SCHEMA,
                )

            opsClient.createNamespace(testNamespace)
            opsClient.createTable(
                tableName = testTable,
                columnNameMapping = columnNameMapping,
                stream = stream,
                replace = false,
            )

            val discoveredSchema = client.discoverSchema(testTable)
            assertEquals(expectedDiscoveredSchema, discoveredSchema)
        }

    /**
     * Test that the connector can correctly compute a schema for a stream containing all data
     * types.
     *
     * @param expectedComputedSchema The schema to expect. This should be the same schema as
     * [discover].
     */
    fun computeSchema(expectedComputedSchema: TableSchema) {
        computeSchema(expectedComputedSchema, Fixtures.ALL_TYPES_MAPPING)
    }

    fun computeSchema(expectedComputedSchema: TableSchema, columnNameMapping: ColumnNameMapping) {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val stream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = Fixtures.ALL_TYPES_SCHEMA,
            )
        val computedSchema = client.computeSchema(stream, columnNameMapping)
        assertEquals(expectedComputedSchema, computedSchema)
    }

    /**
     * Test that the connector correctly detects a no-change situation. This test just creates a
     * table, discovers its schema, and computes a changeset against that same schema.
     */
    fun `noop diff`() {
        `noop diff`(Fixtures.TEST_MAPPING)
    }

    fun `noop diff`(
        columnNameMapping: ColumnNameMapping,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val (_, _, columnChangeset) =
            computeSchemaEvolution(
                testTable,
                Fixtures.TEST_INTEGER_SCHEMA,
                columnNameMapping,
                Fixtures.TEST_INTEGER_SCHEMA,
                columnNameMapping,
            )

        assertTrue(columnChangeset.isNoop(), "Expected changeset to be noop. Got $columnChangeset")
    }

    /** Test that the connector can correctly detect when a new column needs to be added */
    fun `changeset is correct when adding a column`() {
        `changeset is correct when adding a column`(
            initialColumnNameMapping = Fixtures.TEST_MAPPING,
            modifiedColumnNameMapping = Fixtures.ID_AND_TEST_MAPPING
        )
    }

    fun `changeset is correct when adding a column`(
        initialColumnNameMapping: ColumnNameMapping,
        modifiedColumnNameMapping: ColumnNameMapping
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val (_, _, columnChangeset) =
            computeSchemaEvolution(
                testTable,
                Fixtures.TEST_INTEGER_SCHEMA,
                initialColumnNameMapping,
                Fixtures.ID_AND_TEST_SCHEMA,
                modifiedColumnNameMapping,
            )

        // The changeset should indicate that we're trying to add a column
        assertAll(
            {
                assertEquals(
                    columnChangeset.columnsToAdd.keys,
                    setOf(modifiedColumnNameMapping[ID_FIELD]),
                    "Expected to add exactly one column. Got ${columnChangeset.columnsToAdd}"
                )
            },
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToDrop.size,
                    "Expected to not drop any columns. Got ${columnChangeset.columnsToDrop}"
                )
            },
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToChange.size,
                    "Expected to not change any columns. Got ${columnChangeset.columnsToChange}"
                )
            },
            {
                assertEquals(
                    setOf(modifiedColumnNameMapping[TEST_FIELD]),
                    columnChangeset.columnsToRetain.keys,
                    "Expected to retain the original column. Got ${columnChangeset.columnsToRetain}"
                )
            },
        )
    }

    /** Test that the connector can correctly detect when a column needs to be dropped */
    fun `changeset is correct when dropping a column`() {
        `changeset is correct when dropping a column`(
            initialColumnNameMapping = Fixtures.ID_AND_TEST_MAPPING,
            modifiedColumnNameMapping = Fixtures.TEST_MAPPING
        )
    }

    fun `changeset is correct when dropping a column`(
        initialColumnNameMapping: ColumnNameMapping,
        modifiedColumnNameMapping: ColumnNameMapping
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val (_, _, columnChangeset) =
            computeSchemaEvolution(
                testTable,
                Fixtures.ID_AND_TEST_SCHEMA,
                initialColumnNameMapping,
                Fixtures.TEST_INTEGER_SCHEMA,
                modifiedColumnNameMapping,
            )

        // The changeset should indicate that we're trying to drop a column
        assertAll(
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToAdd.size,
                    "Expected to not add any columns. Got ${columnChangeset.columnsToAdd}"
                )
            },
            {
                assertEquals(
                    setOf(initialColumnNameMapping[ID_FIELD]),
                    columnChangeset.columnsToDrop.keys,
                    "Expected to drop exactly one column. Got ${columnChangeset.columnsToDrop}"
                )
            },
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToChange.size,
                    "Expected to not change any columns. Got ${columnChangeset.columnsToChange}"
                )
            },
            {
                assertEquals(
                    setOf(initialColumnNameMapping[TEST_FIELD]),
                    columnChangeset.columnsToRetain.keys,
                    "Expected to retain the original column. Got ${columnChangeset.columnsToRetain}"
                )
            },
        )
    }

    /**
     * Test that the connector can correctly detect when a column's type needs to be changed. Note
     * that this only tests changing the actual type, _not_ changing the column's nullability.
     */
    fun `changeset is correct when changing a column's type`() {
        `changeset is correct when changing a column's type`(Fixtures.TEST_MAPPING)
    }

    fun `changeset is correct when changing a column's type`(
        columnNameMapping: ColumnNameMapping,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val (actualSchema, expectedSchema, columnChangeset) =
            computeSchemaEvolution(
                testTable,
                Fixtures.TEST_INTEGER_SCHEMA,
                columnNameMapping,
                Fixtures.TEST_STRING_SCHEMA,
                columnNameMapping,
            )

        val actualType = actualSchema.columns[columnNameMapping[TEST_FIELD]]!!
        val expectedType = expectedSchema.columns[columnNameMapping[TEST_FIELD]]!!

        // The changeset should indicate that we're trying to drop a column
        assertAll(
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToAdd.size,
                    "Expected to not add any columns. Got ${columnChangeset.columnsToAdd}"
                )
            },
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToDrop.size,
                    "Expected to not drop any columns. Got ${columnChangeset.columnsToDrop}"
                )
            },
            {
                assertEquals(
                    1,
                    columnChangeset.columnsToChange.size,
                    "Expected to change exactly one column. Got ${columnChangeset.columnsToChange}"
                )
            },
            {
                assertEquals(
                    ColumnTypeChange(actualType, expectedType),
                    columnChangeset.columnsToChange[columnNameMapping[TEST_FIELD]],
                    "Expected column to change from $actualType to $expectedType. Got ${columnChangeset.columnsToChange}"
                )
            },
            {
                assertEquals(
                    0,
                    columnChangeset.columnsToRetain.size,
                    "Expected to retain the original column. Got ${columnChangeset.columnsToRetain}"
                )
            },
        )
    }

    fun `basic apply changeset`() {
        `basic apply changeset`(
            initialColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "to_retain" to "to_retain",
                        "to_change" to "to_change",
                        "to_drop" to "to_drop",
                    )
                ),
            modifiedColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "to_retain" to "to_retain",
                        "to_change" to "to_change",
                        "to_add" to "to_add",
                    )
                ),
        )
    }

    /**
     * Execute a basic set of schema changes. We're not changing the sync mode, the types are just
     * string/int (i.e. no JSON), and there's no funky characters anywhere.
     */
    fun `basic apply changeset`(
        initialColumnNameMapping: ColumnNameMapping,
        modifiedColumnNameMapping: ColumnNameMapping
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val initialSchema =
            ObjectType(
                linkedMapOf(
                    "to_retain" to FieldType(StringType, true),
                    "to_change" to FieldType(IntegerType, true),
                    "to_drop" to FieldType(StringType, true),
                ),
            )
        val modifiedSchema =
            ObjectType(
                linkedMapOf(
                    "to_retain" to FieldType(StringType, true),
                    "to_change" to FieldType(StringType, true),
                    "to_add" to FieldType(StringType, true),
                ),
            )
        val modifiedStream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = modifiedSchema,
            )

        // Create the table and compute the schema changeset
        val (_, expectedSchema, changeset) =
            computeSchemaEvolution(
                testTable,
                initialSchema,
                initialColumnNameMapping,
                modifiedSchema,
                modifiedColumnNameMapping,
            )
        // Insert a record before applying the changeset
        testClient.insertRecords(
            testTable,
            initialColumnNameMapping,
            mapOf(
                COLUMN_NAME_AB_RAW_ID to StringValue("fcc784dd-bf06-468e-ad59-666d5aaceae8"),
                COLUMN_NAME_AB_EXTRACTED_AT to TimestampWithTimezoneValue("2025-01-22T00:00:00Z"),
                COLUMN_NAME_AB_META to ObjectValue(linkedMapOf()),
                COLUMN_NAME_AB_GENERATION_ID to IntegerValue(1),
                "to_retain" to StringValue("to_retain original value"),
                "to_change" to IntegerValue(42),
                "to_drop" to StringValue("to_drop original value"),
            ),
        )

        client.applyChangeset(
            modifiedStream,
            modifiedColumnNameMapping,
            testTable,
            expectedSchema.columns,
            changeset,
        )

        val postAlterationRecords = harness.readTableWithoutMetaColumns(testTable)
        Assertions.assertEquals(
            listOf(
                mapOf(
                    "to_retain" to "to_retain original value",
                    // changed from int to string
                    "to_change" to "42",
                    // note the lack of `to_add` - new columns should be initialized to null
                    )
            ),
            postAlterationRecords
                .removeNulls()
                .reverseColumnNameMapping(modifiedColumnNameMapping, airbyteMetaColumnMapping),
        ) {
            "Expected records were not in the overwritten table."
        }

        val postAlterationDiscoveredSchema = client.discoverSchema(testTable)
        val postAlterationChangeset =
            client.computeChangeset(postAlterationDiscoveredSchema.columns, expectedSchema.columns)
        assertTrue(
            postAlterationChangeset.isNoop(),
            "After applying the changeset, we should be a noop against the expected schema"
        )
    }

    /**
     * Utility method for a typical schema evolution test. Creates a table with [initialSchema]
     * using [initialColumnNameMapping], then computes the column changeset using [modifiedSchema]
     * and [modifiedColumnNameMapping]. This method does _not_ actually apply the changeset.
     *
     * Returns a tuple of `(discoveredInitialSchema, computedModifiedSchema, changeset)`.
     */
    private suspend fun computeSchemaEvolution(
        testTable: TableName,
        initialSchema: ObjectType,
        initialColumnNameMapping: ColumnNameMapping,
        modifiedSchema: ObjectType,
        modifiedColumnNameMapping: ColumnNameMapping,
    ): SchemaEvolutionComputation {
        val initialStream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = initialSchema,
            )
        val modifiedStream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = modifiedSchema,
            )

        opsClient.createNamespace(testTable.namespace)
        opsClient.createTable(
            tableName = testTable,
            columnNameMapping = initialColumnNameMapping,
            stream = initialStream,
            replace = false,
        )

        val actualSchema = client.discoverSchema(testTable)
        val expectedSchema = client.computeSchema(modifiedStream, modifiedColumnNameMapping)
        val columnChangeset = client.computeChangeset(actualSchema.columns, expectedSchema.columns)
        return SchemaEvolutionComputation(
            actualSchema,
            expectedSchema,
            columnChangeset,
        )
    }

    data class SchemaEvolutionComputation(
        val discoveredSchema: TableSchema,
        val computedSchema: TableSchema,
        val columnChangeset: ColumnChangeset,
    )
}
