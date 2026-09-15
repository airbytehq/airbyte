/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.table

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.component.TableOperationsClient
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

class BaseDirectLoadInitialStatusGathererTest {

    private val realTableName = TableName("test_namespace", "real_table")
    private val tempTableName = TableName("test_namespace", "real_table_tmp")

    private val stream =
        mockk<DestinationStream> {
            every { tableSchema } returns
                mockk<StreamTableSchema> {
                    every { tableNames } returns
                        TableNames(
                            finalTableName = realTableName,
                            tempTableName = tempTableName,
                        )
                }
        }
    // Mock the catalog to skip its constructor validation, which needs a fully-populated stream.
    private val catalog = mockk<DestinationCatalog> { every { streams } returns listOf(stream) }

    private class TestGatherer(
        client: TableOperationsClient,
        catalog: DestinationCatalog,
    ) : BaseDirectLoadInitialStatusGatherer(client, catalog)

    @Test
    fun `missing table yields null status without counting rows`() = runTest {
        val client = mockk<TableOperationsClient> { coEvery { tableExists(any()) } returns false }

        val status = TestGatherer(client, catalog).gatherInitialStatus()[stream]!!

        assertNull(status.realTable)
        assertNull(status.tempTable)
        // Emptiness must be decided via existence checks, never a full COUNT(*).
        coVerify(exactly = 0) { client.countTable(any()) }
        coVerify(exactly = 0) { client.tableIsEmpty(any()) }
    }

    @Test
    fun `existing empty table is reported as empty`() = runTest {
        val client =
            mockk<TableOperationsClient> {
                coEvery { tableExists(any()) } returns true
                coEvery { tableIsEmpty(any()) } returns true
            }

        val status = TestGatherer(client, catalog).gatherInitialStatus()[stream]!!

        assertEquals(true, status.realTable?.isEmpty)
        assertEquals(true, status.tempTable?.isEmpty)
        coVerify(exactly = 0) { client.countTable(any()) }
    }

    @Test
    fun `existing non-empty table is reported as non-empty`() = runTest {
        val client =
            mockk<TableOperationsClient> {
                coEvery { tableExists(any()) } returns true
                coEvery { tableIsEmpty(any()) } returns false
            }

        val status = TestGatherer(client, catalog).gatherInitialStatus()[stream]!!

        assertEquals(false, status.realTable?.isEmpty)
        assertEquals(false, status.tempTable?.isEmpty)
        coVerify(exactly = 0) { client.countTable(any()) }
    }
}
