/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.client

import com.clickhouse.client.api.Client as ClickHouseClientRaw
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class ClickhouseAirbyteClientTest {
    // Mocks
    private val client: ClickHouseClientRaw = mockk(relaxed = true)
    private val clickhouseSqlGenerator: ClickhouseSqlGenerator = mockk(relaxed = true)

    // Client
    private val clickhouseAirbyteClient = ClickhouseAirbyteClient(client, clickhouseSqlGenerator)

    // Constants
    private val dummySentence = "SELECT 1"

    @Test
    fun testExecute() =
        runTest {
            // TODO: make this test to work with the coroutines

            // val completableFutureMock = mockk<CompletableFuture<CommandResponse>>()
            // coEvery { completableFutureMock.await() } returns mockk()
            // every { client.execute(dummySentence) } returns completableFutureMock
            //
            // clickhouseAirbyteClient.execute(dummySentence)
            //
            // coVerify { client.execute(dummySentence) }
        }

    @Test
    fun testQuery() =
        runTest {
            // TODO: Same than testExecute, make this test to work with the coroutines

            // clickhouseAirbyteClient.query(dummySentence)
            //
            // coVerify { client.query(dummySentence) }
        }
}
