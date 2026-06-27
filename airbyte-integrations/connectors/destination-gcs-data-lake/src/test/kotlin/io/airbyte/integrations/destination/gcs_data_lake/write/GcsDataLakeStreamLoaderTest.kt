/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.iceberg.parquet.toIcebergSchema
import io.airbyte.cdk.load.data.withAirbyteMeta
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
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.BigLakeCatalogConfiguration
import io.airbyte.integrations.destination.gcs_data_lake.spec.generateStagingBranchName
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import kotlin.test.assertEquals
import kotlin.test.assertNotEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.ManageSnapshots
import org.apache.iceberg.Table
import org.apache.iceberg.catalog.Catalog
import org.junit.jupiter.api.Test

internal class GcsDataLakeStreamLoaderTest {

    private val streamStateStore = StreamStateStore<GcsDataLakeStreamState>().also {
        // Mock setup handled per test
    }

    private fun makeTableSchema(schema: ObjectType, importType: ImportType): StreamTableSchema {
        val inputSchema = schema.properties
        return StreamTableSchema(
            columnSchema =
                ColumnSchema(
                    inputSchema = inputSchema,
                    inputToFinalColumnNames = inputSchema.keys.associateWith { it },
                    finalSchema = mapOf(),
                ),
            importType = importType,
            tableNames = TableNames(finalTableName = TableName("namespace", "test")),
        )
    }

    private fun makeAppendStream(
        syncId: Long = 1,
        generationId: Long = 1,
        minimumGenerationId: Long = 0
    ): DestinationStream {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        return DestinationStream(
            generationId = generationId,
            minimumGenerationId = minimumGenerationId,
            syncId = syncId,
            unmappedNamespace = "namespace",
            unmappedName = "name",
            namespaceMapper =
                NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
            tableSchema = makeTableSchema(objectSchema, Append),
        )
    }

    private fun makeIcebergConfiguration(): GcsDataLakeConfiguration {
        return GcsDataLakeConfiguration(
            gcsBucketName = "test-bucket",
            serviceAccountJson = """{"type":"service_account","project_id":"test"}""",
            gcpProjectId = "test-project",
            gcpLocation = "us-central1",
            gcsEndpoint = null,
            namespace = "test_namespace",
            gcsCatalogConfiguration = GcsCatalogConfiguration(
                warehouseLocation = "gs://test-bucket/warehouse",
                mainBranchName = "main",
                catalogConfiguration = BigLakeCatalogConfiguration(
                    catalogName = "test-catalog",
                    gcpLocation = "us-central1",
                ),
            ),
        )
    }

    @Test
    fun testGeneratedStagingBranchNamesUseUuidSuffixWithoutSyncId() {
        val firstBranchName = generateStagingBranchName(makeAppendStream(syncId = 42))
        val retryBranchName = generateStagingBranchName(makeAppendStream(syncId = 43))
        val nextGenerationBranchName =
            generateStagingBranchName(makeAppendStream(syncId = 43, generationId = 2))

        assertEquals(firstBranchName, retryBranchName)
        assertNotEquals(firstBranchName, nextGenerationBranchName)
        assertTrue(firstBranchName.matches(Regex("""airbyte_staging_[0-9a-f_]{36}""")))
        assertTrue(nextGenerationBranchName.matches(Regex("""airbyte_staging_[0-9a-f_]{36}""")))
    }

    @Test
    fun testFailedTeardownPreservesStagingBranchForRecovery() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream = makeAppendStream()
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val icebergConfiguration = makeIcebergConfiguration()
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        every { manageSnapshots.createBranch(any<String>()) } returns manageSnapshots
        every { manageSnapshots.removeBranch(any<String>()) } returns manageSnapshots
        every { manageSnapshots.commit() } just runs
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { manageSnapshots() } returns manageSnapshots
            every { history() } returns emptyList()
        }
        val stateStore = StreamStateStore<GcsDataLakeStreamState>()
        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { createNamespace(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns icebergSchema
        }
        val stagingBranchName = "airbyte_staging_test"
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
                stagingBranchName = stagingBranchName,
                mainBranchName = "main",
                streamStateStore = stateStore,
            )

        runBlocking {
            streamLoader.start()
            streamLoader.teardown(false)
        }

        verify(exactly = 0) { manageSnapshots.removeBranch(stagingBranchName) }
        verify(exactly = 0) { manageSnapshots.replaceBranch("main", stagingBranchName) }
    }

    @Test
    fun testSuccessfulTeardownRemovesStagingBranch() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream = makeAppendStream()
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val icebergConfiguration = makeIcebergConfiguration()
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        val stagingBranchName = "airbyte_staging_test"
        every { manageSnapshots.createBranch(stagingBranchName) } returns manageSnapshots
        every { manageSnapshots.replaceBranch("main", stagingBranchName) } returns manageSnapshots
        every { manageSnapshots.removeBranch(stagingBranchName) } returns manageSnapshots
        every { manageSnapshots.commit() } just runs
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { refresh() } just runs
            every { manageSnapshots() } returns manageSnapshots
            every { history() } returns emptyList()
        }
        val stateStore = StreamStateStore<GcsDataLakeStreamState>()
        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { createNamespace(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns icebergSchema
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
                stagingBranchName = stagingBranchName,
                mainBranchName = "main",
                streamStateStore = stateStore,
            )

        runBlocking {
            streamLoader.start()
            streamLoader.teardown(true)
        }

        verify { manageSnapshots.replaceBranch("main", stagingBranchName) }
        verify { manageSnapshots.removeBranch(stagingBranchName) }
    }

    @Test
    fun testStartStoresStagingBranchNameInStreamState() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream = makeAppendStream()
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val icebergConfiguration = makeIcebergConfiguration()
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        val stagingBranchName = "airbyte_staging_unique_123"
        every { manageSnapshots.createBranch(stagingBranchName) } returns manageSnapshots
        every { manageSnapshots.commit() } just runs
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { manageSnapshots() } returns manageSnapshots
            every { history() } returns emptyList()
        }
        val stateStore = StreamStateStore<GcsDataLakeStreamState>()
        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { createNamespace(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns icebergSchema
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
                stagingBranchName = stagingBranchName,
                mainBranchName = "main",
                streamStateStore = stateStore,
            )

        runBlocking {
            streamLoader.start()
        }

        val state = stateStore.get(stream.mappedDescriptor)!!
        assertEquals(stagingBranchName, state.stagingBranchName)
    }

    @Test
    fun testCompletedTeardownPreservesStagingBranchWhenPromotionFails() {
        val objectSchema =
            ObjectType(
                linkedMapOf(
                    "id" to FieldType(IntegerType, nullable = true),
                    "name" to FieldType(StringType, nullable = true),
                ),
            )
        val stream = makeAppendStream()
        val icebergSchema = objectSchema.withAirbyteMeta(true).toIcebergSchema(emptyList())
        val icebergConfiguration = makeIcebergConfiguration()
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        val stagingBranchName = "airbyte_staging_test"
        var commitCount = 0
        every { manageSnapshots.createBranch(stagingBranchName) } returns manageSnapshots
        every { manageSnapshots.replaceBranch("main", stagingBranchName) } returns manageSnapshots
        every { manageSnapshots.removeBranch(stagingBranchName) } returns manageSnapshots
        every { manageSnapshots.commit() } answers {
            commitCount += 1
            if (commitCount == 2) {
                throw RuntimeException("promotion failed")
            }
        }
        val table: Table = mockk {
            every { schema() } returns icebergSchema
            every { refresh() } just runs
            every { manageSnapshots() } returns manageSnapshots
            every { history() } returns emptyList()
        }
        val stateStore = StreamStateStore<GcsDataLakeStreamState>()
        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { createNamespace(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns icebergSchema
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
                stagingBranchName = stagingBranchName,
                mainBranchName = "main",
                streamStateStore = stateStore,
            )

        val failure =
            assertFailsWith<RuntimeException> {
                runBlocking {
                    streamLoader.start()
                    streamLoader.teardown(true)
                }
            }

        assertEquals("promotion failed", failure.message)
        verify { manageSnapshots.replaceBranch("main", stagingBranchName) }
        verify(exactly = 0) { manageSnapshots.removeBranch(stagingBranchName) }
    }
}
