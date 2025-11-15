/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.component

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsFixtures as Fixtures
import io.airbyte.cdk.load.component.TableOperationsFixtures.ID_FIELD
import io.airbyte.cdk.load.component.TableOperationsFixtures.TEST_FIELD
import io.airbyte.cdk.load.component.TableOperationsFixtures.inputRecord
import io.airbyte.cdk.load.component.TableOperationsFixtures.insertRecords
import io.airbyte.cdk.load.component.TableOperationsFixtures.removeNulls
import io.airbyte.cdk.load.component.TableOperationsFixtures.reverseColumnNameMapping
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.table.ColumnNameMapping
import io.airbyte.cdk.load.table.TableName
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.assertAll
import org.junit.jupiter.params.provider.Arguments.argumentSet

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
     * [`computeSchema handles all data types`].
     */
    fun `discover recognizes all data types`(expectedDiscoveredSchema: TableSchema) {
        `discover recognizes all data types`(expectedDiscoveredSchema, Fixtures.ALL_TYPES_MAPPING)
    }

    fun `discover recognizes all data types`(
        expectedDiscoveredSchema: TableSchema,
        columnNameMapping: ColumnNameMapping
    ) = runTest {
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
     * [`discover recognizes all data types`].
     */
    fun `computeSchema handles all data types`(expectedComputedSchema: TableSchema) {
        `computeSchema handles all data types`(expectedComputedSchema, Fixtures.ALL_TYPES_MAPPING)
    }

    fun `computeSchema handles all data types`(
        expectedComputedSchema: TableSchema,
        columnNameMapping: ColumnNameMapping
    ) {
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

    /**
     * Execute a basic set of schema changes, across a variety of sync modes. The types are just
     * string/int (i.e. no JSON), and there's no funky characters anywhere.
     *
     * You likely will annotate your test method as:
     * ```kotlin
     * @ParameterizedTest
     * @MethodSource("io.airbyte.cdk.load.component.TableSchemaEvolutionSuite#applyChangesetArguments")
     * ```
     */
    fun `apply changeset`(
        initialStreamIsDedup: Boolean,
        modifiedStreamIsDedup: Boolean,
    ) {
        `apply changeset`(
            initialColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "id" to "id",
                        "updated_at" to "updated_at",
                        "to_retain" to "to_retain",
                        "to_change" to "to_change",
                        "to_drop" to "to_drop",
                    )
                ),
            modifiedColumnNameMapping =
                ColumnNameMapping(
                    mapOf(
                        "id" to "id",
                        "updated_at" to "updated_at",
                        "to_retain" to "to_retain",
                        "to_change" to "to_change",
                        "to_add" to "to_add",
                    )
                ),
            initialStreamIsDedup,
            modifiedStreamIsDedup,
        )
    }

    fun `apply changeset`(
        initialColumnNameMapping: ColumnNameMapping,
        modifiedColumnNameMapping: ColumnNameMapping,
        initialStreamIsDedup: Boolean,
        modifiedStreamIsDedup: Boolean,
    ) = runTest {
        val testNamespace = Fixtures.generateTestNamespace("namespace-test")
        val testTable = Fixtures.generateTestTableName("table-test-table", testNamespace)
        val initialSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, true),
                    "updated_at" to FieldType(IntegerType, true),
                    "to_retain" to FieldType(StringType, true),
                    "to_change" to FieldType(IntegerType, true),
                    "to_drop" to FieldType(StringType, true),
                ),
            )
        val initialStream =
            Fixtures.createSimpleStream(
                testTable.namespace,
                testTable.name,
                initialSchema,
                initialStreamIsDedup,
            )
        val modifiedSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, true),
                    "updated_at" to FieldType(IntegerType, true),
                    "to_retain" to FieldType(StringType, true),
                    "to_change" to FieldType(StringType, true),
                    "to_add" to FieldType(StringType, true),
                ),
            )
        val modifiedStream =
            Fixtures.createSimpleStream(
                testTable.namespace,
                testTable.name,
                modifiedSchema,
                modifiedStreamIsDedup,
            )

        // Create the table and compute the schema changeset
        val (_, expectedSchema, changeset) =
            computeSchemaEvolution(
                testTable,
                initialSchema,
                initialColumnNameMapping,
                modifiedSchema,
                modifiedColumnNameMapping,
                initialStream,
                modifiedStream,
            )
        // Insert a record before applying the changeset
        testClient.insertRecords(
            testTable,
            initialColumnNameMapping,
            inputRecord(
                "fcc784dd-bf06-468e-ad59-666d5aaceae8",
                "2025-01-22T00:00:00Z",
                linkedMapOf(),
                1,
                "id" to IntegerValue(1234),
                "updated_at" to IntegerValue(5678),
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
                    "id" to 1234L,
                    "updated_at" to 5678L,
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
        initialStream: DestinationStream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = initialSchema,
            ),
        modifiedStream: DestinationStream =
            Fixtures.createAppendStream(
                namespace = testTable.namespace,
                name = testTable.name,
                schema = modifiedSchema,
            ),
    ): SchemaEvolutionComputation {
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

    companion object {
        // junit needs everything annotated with JvmStatic, and doesn't support backtick-quoted
        // names
        @JvmStatic
        fun applyChangesetArguments() =
            listOf(
                argumentSet("append -> append", false, false),
                argumentSet("append -> dedup", false, true),
                argumentSet("dedup -> append", true, false),
                argumentSet("dedup -> dedup", true, true),
            )
    }
}
