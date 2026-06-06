/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake.write

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.toolkits.iceberg.parquet.ColumnTypeChangeBehavior
import io.airbyte.cdk.load.toolkits.iceberg.parquet.IcebergTableSynchronizer
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SchemaUpdateResult
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.airbyte.cdk.load.write.StreamStateStore
import io.airbyte.integrations.destination.gcs_data_lake.catalog.GcsDataLakeCatalogUtil
import io.airbyte.integrations.destination.gcs_data_lake.spec.DEFAULT_STAGING_BRANCH
import io.airbyte.integrations.destination.gcs_data_lake.spec.GcsDataLakeConfiguration
import io.mockk.clearMocks
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.runs
import io.mockk.verify
import io.mockk.verifyOrder
import kotlinx.coroutines.runBlocking
import org.apache.iceberg.ManageSnapshots
import org.apache.iceberg.Schema
import org.apache.iceberg.SnapshotRef
import org.apache.iceberg.Table
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.types.Types
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

internal class GcsDataLakeStreamLoaderTest {
    private val streamStateStore: StreamStateStore<GcsDataLakeStreamState> = mockk {
        every { put(any(), any()) } returns Unit
    }

    private val emptyTableSchema =
        StreamTableSchema(
            columnSchema =
                ColumnSchema(
                    inputSchema = mapOf(),
                    inputToFinalColumnNames = mapOf(),
                    finalSchema = mapOf(),
                ),
            importType = Append,
            tableNames = TableNames(finalTableName = TableName("namespace", "test")),
        )

    @Test
    fun testOptInDeletesStagingBranchAfterSuccessfulTeardown() {
        val fixture = createMinimalStartedLoader(deleteStagingBranchOnSuccess = true)

        runBlocking { fixture.streamLoader.teardown(true) }

        verifyOrder {
            fixture.table.refresh()
            fixture.manageSnapshots.replaceBranch("main", DEFAULT_STAGING_BRANCH)
            fixture.manageSnapshots.commit()
            fixture.table.refresh()
            fixture.manageSnapshots.removeBranch(DEFAULT_STAGING_BRANCH)
            fixture.manageSnapshots.commit()
        }
    }

    @Test
    fun testDefaultLeavesStagingBranchAfterSuccessfulTeardown() {
        val fixture = createMinimalStartedLoader(deleteStagingBranchOnSuccess = false)

        runBlocking { fixture.streamLoader.teardown(true) }

        verify(exactly = 0) {
            fixture.manageSnapshots.removeBranch(any())
        }
    }

    @Test
    fun testFailedSyncLeavesStagingBranch() {
        val fixture = createMinimalStartedLoader(deleteStagingBranchOnSuccess = true)

        runBlocking { fixture.streamLoader.teardown(false) }

        verify(exactly = 0) {
            fixture.manageSnapshots.removeBranch(any())
        }
        verify(exactly = 0) { fixture.manageSnapshots.replaceBranch(any<String>(), any<String>()) }
    }

    @Test
    fun testStagingBranchDeletionFailureDoesNotFailTeardown() {
        val fixture = createMinimalStartedLoader(deleteStagingBranchOnSuccess = true)
        every { fixture.manageSnapshots.removeBranch(DEFAULT_STAGING_BRANCH) } throws
            RuntimeException("catalog failure")

        assertDoesNotThrow { runBlocking { fixture.streamLoader.teardown(true) } }

        verify(exactly = 1) { fixture.manageSnapshots.removeBranch(DEFAULT_STAGING_BRANCH) }
    }

    private data class MinimalLoaderFixture(
        val streamLoader: GcsDataLakeStreamLoader,
        val table: Table,
        val manageSnapshots: ManageSnapshots,
    )

    private fun createMinimalStartedLoader(
        deleteStagingBranchOnSuccess: Boolean
    ): MinimalLoaderFixture {
        val schema = Schema(Types.NestedField.of(1, true, "id", Types.LongType.get()))
        val stream =
            DestinationStream(
                generationId = 1,
                minimumGenerationId = 0,
                syncId = 1,
                unmappedNamespace = "namespace",
                unmappedName = "name",
                namespaceMapper =
                    NamespaceMapper(namespaceDefinitionType = NamespaceDefinitionType.SOURCE),
                tableSchema = emptyTableSchema,
            )
        val catalog: Catalog = mockk()
        val manageSnapshots: ManageSnapshots = mockk()
        val table: Table = mockk {
            every { schema() } returns schema
            every { refresh() } just runs
            every { refs() } returnsMany
                listOf(emptyMap(), mapOf(DEFAULT_STAGING_BRANCH to mockk<SnapshotRef>()))
            every { manageSnapshots() } returns manageSnapshots
        }
        every { manageSnapshots.createBranch(DEFAULT_STAGING_BRANCH) } returns manageSnapshots
        every { manageSnapshots.replaceBranch("main", DEFAULT_STAGING_BRANCH) } returns
            manageSnapshots
        every { manageSnapshots.removeBranch(DEFAULT_STAGING_BRANCH) } returns manageSnapshots
        every { manageSnapshots.commit() } just runs

        val gcsDataLakeCatalogUtil: GcsDataLakeCatalogUtil = mockk {
            every { createNamespace(any(), any()) } just runs
            every { toCatalogProperties(any()) } returns mapOf()
        }
        val icebergUtil: IcebergUtil = mockk {
            every { createCatalog(any(), any()) } returns catalog
            every { createTable(any(), any(), any()) } returns table
            every { toIcebergSchema(any()) } returns schema
        }
        val icebergTableSynchronizer: IcebergTableSynchronizer = mockk {
            every {
                maybeApplySchemaChanges(
                    any(),
                    any(),
                    ColumnTypeChangeBehavior.SAFE_SUPERTYPE,
                    true
                )
            } returns SchemaUpdateResult(schema, emptyList())
        }
        val streamLoader =
            GcsDataLakeStreamLoader(
                icebergConfiguration = mockk<GcsDataLakeConfiguration>(),
                stream = stream,
                icebergTableSynchronizer = icebergTableSynchronizer,
                gcsDataLakeCatalogUtil = gcsDataLakeCatalogUtil,
                icebergUtil = icebergUtil,
                stagingBranchName = DEFAULT_STAGING_BRANCH,
                mainBranchName = "main",
                deleteStagingBranchOnSuccess = deleteStagingBranchOnSuccess,
                streamStateStore = streamStateStore,
            )
        runBlocking { streamLoader.start() }
        clearMocks(table, manageSnapshots, answers = false)
        every { table.refs() } returns mapOf(DEFAULT_STAGING_BRANCH to mockk<SnapshotRef>())

        return MinimalLoaderFixture(streamLoader, table, manageSnapshots)
    }
}
