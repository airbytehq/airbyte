/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.io

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergTableCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.io.IcebergUtil
import io.mockk.Runs
import io.mockk.called
import io.mockk.every
import io.mockk.just
import io.mockk.mockk
import io.mockk.verify
import org.apache.iceberg.DeleteFiles
import org.apache.iceberg.FileScanTask
import org.apache.iceberg.Table
import org.apache.iceberg.aws.s3.S3FileIO
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.io.CloseableIterable
import org.apache.iceberg.io.CloseableIterator
import org.apache.iceberg.io.FileIO
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertDoesNotThrow

internal class S3DataLakeTableCleanerTest {
    private fun mockStream(
        importType: ImportType = Append,
        generationId: Long = 1,
        minimumGenerationId: Long = 0
    ) =
        DestinationStream(
            unmappedNamespace = "testing",
            unmappedName = "test",
            importType = importType,
            schema = ObjectTypeWithoutSchema,
            generationId = generationId,
            minimumGenerationId = minimumGenerationId,
            syncId = 1,
            namespaceMapper = NamespaceMapper()
        )

    @Test
    fun testClearingTableWithPrefix() {
        val catalog: Catalog = mockk { every { dropTable(any(), true) } returns true }
        val icebergUtil: IcebergUtil = mockk()
        val tableIdentifier: TableIdentifier = mockk()
        val fileIo: S3FileIO = mockk { every { deletePrefix(any()) } returns Unit }
        val tableLocation = "table/location"

        val cleaner = IcebergTableCleaner(icebergUtil)

        cleaner.clearTable(
            catalog = catalog,
            identifier = tableIdentifier,
            io = fileIo,
            tableLocation = tableLocation
        )

        verify(exactly = 1) { catalog.dropTable(tableIdentifier, true) }
        verify(exactly = 1) { fileIo.deletePrefix(tableLocation) }
    }

    @Test
    fun testClearingTableWithoutPrefix() {
        val catalog: Catalog = mockk { every { dropTable(any(), true) } returns true }
        val icebergUtil: IcebergUtil = mockk()
        val tableIdentifier: TableIdentifier = mockk()
        val fileIo: FileIO = mockk()
        val tableLocation = "table/location"

        val cleaner = IcebergTableCleaner(icebergUtil)

        cleaner.clearTable(
            catalog = catalog,
            identifier = tableIdentifier,
            io = fileIo,
            tableLocation = tableLocation
        )

        verify(exactly = 1) { catalog.dropTable(tableIdentifier, true) }
        verify { fileIo wasNot called }
    }

    @Test
    fun `deleteIrrelevantGenerationId handles empty scan results gracefully`() {
        val stream = mockStream()
        val icebergUtil: IcebergUtil = mockk {
            every { constructGenerationIdSuffix(any<DestinationStream>()) } returns
                "ab-generation-id-1-e"
        }
        val cleaner = IcebergTableCleaner(icebergUtil)

        val tasks = CloseableIterable.empty<FileScanTask>()
        val table = mockk<Table>()
        every { table.newScan().planFiles() } returns tasks

        assertDoesNotThrow { cleaner.deleteOldGenerationData(table, "staging", stream) }
        verify(exactly = 0) { table.newDelete() }
    }

    @Test
    fun `deleteIrrelevantGenerationId deletes matching file via deleteFile`() {
        val stream = mockStream()
        val icebergUtil: IcebergUtil = mockk {
            every { constructGenerationIdSuffix(any<DestinationStream>()) } returns
                "ab-generation-id-1-e"
        }
        val cleaner = IcebergTableCleaner(icebergUtil)
        val filePathToDelete = "path/to/gen-5678/foo-bar-ab-generation-id-0-e.parquet"
        val fileScanTask = mockk<FileScanTask>()
        val table = mockk<Table>()

        val tasks = mockk<CloseableIterable<FileScanTask>>()
        every { tasks.iterator() } returns
            CloseableIterator.withClose(listOf(fileScanTask).iterator())
        every { tasks.close() } just Runs
        every { table.newScan().planFiles() } returns tasks

        every { fileScanTask.file().location() } returns filePathToDelete

        val delete = mockk<DeleteFiles>()
        every { table.newDelete().toBranch("staging") } returns delete
        every { delete.deleteFile(filePathToDelete) } returns delete
        every { delete.commit() } just Runs

        assertDoesNotThrow { cleaner.deleteOldGenerationData(table, "staging", stream) }

        verify {
            table.newDelete().toBranch(eq("staging"))
            delete.deleteFile(filePathToDelete)
            delete.commit()
        }
    }

    @Test
    fun `deleteIrrelevantGenerationId deletes files with missing generation id prefix`() {
        val stream = mockStream()
        val icebergUtil: IcebergUtil = mockk {
            every { constructGenerationIdSuffix(any<DestinationStream>()) } returns
                "ab-generation-id-1-e"
        }
        val cleaner = IcebergTableCleaner(icebergUtil)
        val filePathToDelete = "path/to/gen-5678/compacted-file.parquet"
        val fileScanTask = mockk<FileScanTask>()
        val table = mockk<Table>()

        val tasks = mockk<CloseableIterable<FileScanTask>>()
        every { tasks.iterator() } returns
            CloseableIterator.withClose(listOf(fileScanTask).iterator())
        every { tasks.close() } just Runs
        every { table.newScan().planFiles() } returns tasks

        every { fileScanTask.file().location() } returns filePathToDelete

        val delete = mockk<DeleteFiles>()
        every { table.newDelete().toBranch("staging") } returns delete
        every { delete.deleteFile(filePathToDelete) } returns delete
        every { delete.commit() } just Runs

        assertDoesNotThrow { cleaner.deleteOldGenerationData(table, "staging", stream) }

        verify {
            table.newDelete().toBranch(eq("staging"))
            delete.deleteFile(filePathToDelete)
            delete.commit()
        }
    }
}
