/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergSuperTypeFinder
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTypesComparator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.Schema
import org.apache.iceberg.Table
import org.apache.iceberg.UpdateSchema
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

internal class GcsDataLakeStreamLoaderTest {

    @MockK(relaxed = true)
    private lateinit var streamStateStore: StreamStateStore<GcsDataLakeStreamState>

    @BeforeEach
    fun setup() {
        every { streamStateStore.put(any(), any()) } returns Unit
    }

    /**
     * Tests the fix for the bug where setIdentifierFields fails with
     * IllegalArgumentException when the PK field is optional in the existing table.
     * The fix ensures requireColumn() is called for each PK field before setIdentifierFields().
     */
    @Test
    fun testStartCallsRequireColumnBeforeSetIdentifierFields() {
        val primaryKeys = listOf("transactionReference")
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "transactionReference" to FieldType(StringType, nullable = false),
                    "amount" to FieldType(IntegerType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "test_stream",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema =
                    makeTableSchema(
                        objectSchema,
                        Dedupe(primaryKey = listOf(primaryKeys), cursor = primaryKeys)
                    ),
            )

        // Simulate a pre-existing table where the PK field is OPTIONAL
        // (as BigLake may create it). This is the scenario that triggers the bug.
        val existingTableSchema =
            Schema(
                listOf(
                    Types.NestedField.optional(1, "transactionReference", Types.StringType.get()),
                    Types.NestedField.optional(2, "amount", Types.LongType.get()),
                    Types.NestedField.required(
                        3,
                        Meta.COLUMN_NAME_AB_RAW_ID,
                        Types.StringType.get()
                    ),
                    Types.NestedField.required(
                        4,
                        Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                        Types.LongType.get()
                    ),
                    Types.NestedField.required(
                        5,
                        Meta.COLUMN_NAME_AB_META,
                        Types.StructType.of(
                            Types.NestedField.required(6, "sync_id", Types.LongType.get()),
                            Types.NestedField.required(
                                7,
                                "changes",
                                Types.ListType.ofRequired(
                                    8,
                                    Types.StructType.of(
                                        Types.NestedField.required(
                                            9,
                                            "field",
                                            Types.StringType.get()
                                        ),
                                        Types.NestedField.required(
                                            10,
                                            "change",
                                            Types.StringType.get(),
                                        ),
                                        Types.NestedField.required(
                                            11,
                                            "reason",
                                            Types.StringType.get(),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    Types.NestedField.required(
                        12,
                        Meta.COLUMN_NAME_AB_GENERATION_ID,
                        Types.LongType.get()
                    ),
                ),
                emptySet(), // No identifier fields set yet
            )

        val icebergConfiguration: GcsDataLakeConfiguration = mockk(relaxed = true)
        val catalog: Catalog = mockk()

        val updateSchema: UpdateSchema = mockk()
        every { updateSchema.requireColumn("transactionReference") } returns updateSchema
        every { updateSchema.setIdentifierFields(primaryKeys) } returns updateSchema
        every { updateSchema.commit() } just runs

        val table: Table = mockk {
            every { schema() } returns existingTableSchema
            every { history() } returns emptyList()
            every { updateSchema() } returns updateSchema
            every { refresh() } just runs
            every { manageSnapshots().createBranch(any()).commit() } just runs
        }

        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { toCatalogProperties(any()) } returns mapOf()
            every { createNamespace(any(), any()) } just runs
        }

        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns existingTableSchema
        }

        val streamLoader =
            GcsDataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                gcsDataLakeCatalogUtil,
                icebergUtil,
                stagingBranchName = "airbyte_staging",
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )

        runBlocking { streamLoader.start() }

        // Verify that requireColumn is called BEFORE setIdentifierFields
        verify(exactly = 1) { updateSchema.requireColumn("transactionReference") }
        verify(exactly = 1) { updateSchema.setIdentifierFields(primaryKeys) }
        verify(exactly = 1) { updateSchema.commit() }
    }

    @Test
    fun testStartCallsRequireColumnForMultiplePrimaryKeys() {
        val primaryKeys = listOf("org_id", "transaction_id")
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "org_id" to FieldType(StringType, nullable = false),
                    "transaction_id" to FieldType(StringType, nullable = false),
                    "amount" to FieldType(IntegerType, nullable = true),
                ),
            )
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "test_stream",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema =
                    makeTableSchema(
                        objectSchema,
                        Dedupe(primaryKey = listOf(listOf("org_id"), listOf("transaction_id")), cursor = listOf("org_id"))
                    ),
            )

        val existingTableSchema =
            Schema(
                listOf(
                    Types.NestedField.optional(1, "org_id", Types.StringType.get()),
                    Types.NestedField.optional(2, "transaction_id", Types.StringType.get()),
                    Types.NestedField.optional(3, "amount", Types.LongType.get()),
                    Types.NestedField.required(
                        4,
                        Meta.COLUMN_NAME_AB_RAW_ID,
                        Types.StringType.get()
                    ),
                    Types.NestedField.required(
                        5,
                        Meta.COLUMN_NAME_AB_EXTRACTED_AT,
                        Types.LongType.get()
                    ),
                    Types.NestedField.required(
                        6,
                        Meta.COLUMN_NAME_AB_META,
                        Types.StructType.of(
                            Types.NestedField.required(7, "sync_id", Types.LongType.get()),
                            Types.NestedField.required(
                                8,
                                "changes",
                                Types.ListType.ofRequired(
                                    9,
                                    Types.StructType.of(
                                        Types.NestedField.required(
                                            10,
                                            "field",
                                            Types.StringType.get()
                                        ),
                                        Types.NestedField.required(
                                            11,
                                            "change",
                                            Types.StringType.get(),
                                        ),
                                        Types.NestedField.required(
                                            12,
                                            "reason",
                                            Types.StringType.get(),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    Types.NestedField.required(
                        13,
                        Meta.COLUMN_NAME_AB_GENERATION_ID,
                        Types.LongType.get()
                    ),
                ),
                emptySet(),
            )

        val icebergConfiguration: GcsDataLakeConfiguration = mockk(relaxed = true)
        val catalog: Catalog = mockk()

        val updateSchema: UpdateSchema = mockk()
        every { updateSchema.requireColumn("org_id") } returns updateSchema
        every { updateSchema.requireColumn("transaction_id") } returns updateSchema
        every { updateSchema.setIdentifierFields(primaryKeys) } returns updateSchema
        every { updateSchema.commit() } just runs

        val table: Table = mockk {
            every { schema() } returns existingTableSchema
            every { history() } returns emptyList()
            every { updateSchema() } returns updateSchema
            every { refresh() } just runs
            every { manageSnapshots().createBranch(any()).commit() } just runs
        }

        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { toCatalogProperties(any()) } returns mapOf()
            every { createNamespace(any(), any()) } just runs
        }

        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns existingTableSchema
        }

        val streamLoader =
            GcsDataLakeStreamLoader(
                icebergConfiguration,
                stream,
                IcebergTableSynchronizer(
                    IcebergTypesComparator(),
                    IcebergSuperTypeFinder(IcebergTypesComparator()),
                ),
                gcsDataLakeCatalogUtil,
                icebergUtil,
                stagingBranchName = "airbyte_staging",
                mainBranchName = "main",
                streamStateStore = streamStateStore,
            )

        runBlocking { streamLoader.start() }

        verify(exactly = 1) { updateSchema.requireColumn("org_id") }
        verify(exactly = 1) { updateSchema.requireColumn("transaction_id") }
        verify(exactly = 1) { updateSchema.setIdentifierFields(primaryKeys) }
        verify(exactly = 1) { updateSchema.commit() }
    }

    private fun makeTableSchema(
        schema: ObjectType,
        importType: io.airbyte.cdk.load.command.ImportType,
    ): StreamTableSchema {
        val inputSchema = schema.properties
        return StreamTableSchema(
            columnSchema =
                ColumnSchema(
                    inputSchema = inputSchema,
                    inputToFinalColumnNames = inputSchema.keys.associateWith { it },
                    finalSchema = mapOf(),
                ),
            importType = importType,
            tableNames = TableNames(finalTableName = TableName("namespace", "test_stream")),
        )
    }
}
