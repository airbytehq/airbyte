/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2.io

import io.mockk.called
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import org.apache.iceberg.aws.s3.S3FileIO
import org.apache.iceberg.catalog.Catalog
import org.apache.iceberg.catalog.TableIdentifier
import org.apache.iceberg.io.FileIO
import org.junit.jupiter.api.Test

internal class IcebergTableCleanerTest {

    @Test
    fun testClearingTableWithPrefix() {
        val catalog: Catalog = mockk { every { dropTable(any(), true) } returns true }
        val tableIdentifier: TableIdentifier = mockk()
        val fileIo: S3FileIO = mockk { every { deletePrefix(any()) } returns Unit }
        val tableLocation = "table/location"

        val cleaner = IcebergTableCleaner()

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
        val tableIdentifier: TableIdentifier = mockk()
        val fileIo: FileIO = mockk()
        val tableLocation = "table/location"

        val cleaner = IcebergTableCleaner()

        cleaner.clearTable(
            catalog = catalog,
            identifier = tableIdentifier,
            io = fileIo,
            tableLocation = tableLocation
        )

        verify(exactly = 1) { catalog.dropTable(tableIdentifier, true) }
        verify { fileIo wasNot called }
    }
}
