/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.client

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.table.directload.DirectLoadTableStatus
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

internal class RedshiftInitialStatusGathererTest {

    private val realTable = TableName(namespace = "ns", name = "real_table")
    private val tempTable = TableName(namespace = "ns", name = "temp_table")

    private fun mockStream(): DestinationStream {
        val tableNames = TableNames(finalTableName = realTable, tempTableName = tempTable)
        val schema = mockk<StreamTableSchema> { every { this@mockk.tableNames } returns tableNames }
        return mockk { every { tableSchema } returns schema }
    }

    private fun buildGatherer(
        client: RedshiftAirbyteClient,
        streams: List<DestinationStream>,
    ): RedshiftInitialStatusGatherer {
        val catalog = mockk<DestinationCatalog> { every { this@mockk.streams } returns streams }
        return RedshiftInitialStatusGatherer(client, catalog)
    }

    @Test
    fun `gatherInitialStatus uses isTableNotEmpty instead of countTable`() = runTest {
        val stream = mockStream()
        val client = mockk<RedshiftAirbyteClient>()
        coEvery { client.isTableNotEmpty(realTable) } returns true
        coEvery { client.isTableNotEmpty(tempTable) } returns false

        val gatherer = buildGatherer(client, listOf(stream))
        val result = gatherer.gatherInitialStatus()

        val status = result[stream]!!
        assertFalse(status.realTable!!.isEmpty)
        assertTrue(status.tempTable!!.isEmpty)

        // Verify isTableNotEmpty was called (not countTable)
        coVerify(exactly = 1) { client.isTableNotEmpty(realTable) }
        coVerify(exactly = 1) { client.isTableNotEmpty(tempTable) }
    }

    @Test
    fun `gatherInitialStatus returns null for missing tables`() = runTest {
        val stream = mockStream()
        val client = mockk<RedshiftAirbyteClient>()
        coEvery { client.isTableNotEmpty(realTable) } returns null
        coEvery { client.isTableNotEmpty(tempTable) } returns null

        val gatherer = buildGatherer(client, listOf(stream))
        val result = gatherer.gatherInitialStatus()

        val status = result[stream]!!
        assertNull(status.realTable)
        assertNull(status.tempTable)
    }

    @Test
    fun `gatherInitialStatus handles mixed table states`() = runTest {
        val stream = mockStream()
        val client = mockk<RedshiftAirbyteClient>()
        // Real table exists and has data, temp table doesn't exist
        coEvery { client.isTableNotEmpty(realTable) } returns true
        coEvery { client.isTableNotEmpty(tempTable) } returns null

        val gatherer = buildGatherer(client, listOf(stream))
        val result = gatherer.gatherInitialStatus()

        val status = result[stream]!!
        assertEquals(DirectLoadTableStatus(isEmpty = false), status.realTable)
        assertNull(status.tempTable)
    }

    @Test
    fun `gatherInitialStatus handles multiple streams concurrently`() = runTest {
        val stream1 = mockStream()
        val realTable2 = TableName(namespace = "ns", name = "real_table_2")
        val tempTable2 = TableName(namespace = "ns", name = "temp_table_2")
        val stream2 =
            mockk<DestinationStream> {
                every { tableSchema } returns
                    mockk {
                        every { tableNames } returns
                            TableNames(finalTableName = realTable2, tempTableName = tempTable2)
                    }
            }

        val client = mockk<RedshiftAirbyteClient>()
        coEvery { client.isTableNotEmpty(realTable) } returns true
        coEvery { client.isTableNotEmpty(tempTable) } returns false
        coEvery { client.isTableNotEmpty(realTable2) } returns null
        coEvery { client.isTableNotEmpty(tempTable2) } returns true

        val gatherer = buildGatherer(client, listOf(stream1, stream2))
        val result = gatherer.gatherInitialStatus()

        assertEquals(2, result.size)

        val status1 = result[stream1]!!
        assertFalse(status1.realTable!!.isEmpty)
        assertTrue(status1.tempTable!!.isEmpty)

        val status2 = result[stream2]!!
        assertNull(status2.realTable)
        assertFalse(status2.tempTable!!.isEmpty)
    }
}
