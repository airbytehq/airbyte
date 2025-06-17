/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse_v2.write.direct

import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.write.DirectLoader
import io.airbyte.integrations.destination.clickhouse_v2.write.RecordMunger
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.junit5.MockKExtension
import io.mockk.mockk
import io.mockk.verify
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class ClickhouseDirectLoaderTest {
    @MockK(relaxed = true) lateinit var munger: RecordMunger

    @MockK(relaxed = true) lateinit var buffer: BinaryRowInsertBuffer

    private lateinit var loader: ClickhouseDirectLoader

    @BeforeEach
    fun setup() {
        every { munger.transformForDest(any()) } returns Fixtures.mungedRecord
        loader = ClickhouseDirectLoader(munger, buffer)
    }

    @Test
    fun `incomplete case - #accept munges and accumulates record`() = runTest {
        val input = mockk<DestinationRecordRaw>(relaxed = true)
        val result = loader.accept(input)

        assertEquals(DirectLoader.Incomplete, result)
        verify { munger.transformForDest(input) }
        verify { buffer.accumulate(Fixtures.mungedRecord) }
        coVerify(exactly = 0) { buffer.flush() }
    }

    @Test
    fun `complete case 1 - #accept munges and accumulates record then flushes buffer when accumulated bytes hits threshold`() =
        runTest {
            val bytes = ClickhouseDirectLoader.Constants.MAX_BATCH_SIZE_BYTES
            val input = mockk<DestinationRecordRaw> { every { serializedSizeBytes } returns bytes }
            val result = loader.accept(input)

            verify { munger.transformForDest(input) }
            verify { buffer.accumulate(Fixtures.mungedRecord) }
            coVerify(exactly = 1) { buffer.flush() }

            assertEquals(DirectLoader.Complete, result)
        }

    @Test
    fun `complete case 2 - #accept munges and accumulates record then flushes buffer when accumulated record count hits threshold`() =
        runTest {
            val input = mockk<DestinationRecordRaw>(relaxed = true)

            // fill the batch minuses one
            val batchSize = ClickhouseDirectLoader.Constants.MAX_BATCH_SIZE_RECORDS.toInt()
            var result: DirectLoader.DirectLoadResult = DirectLoader.Incomplete
            repeat(batchSize - 1) { result = loader.accept(input) }
            // we're still incomplete
            assertEquals(DirectLoader.Incomplete, result)

            // complete the batch
            result = loader.accept(input)

            assertEquals(DirectLoader.Complete, result)
            verify(exactly = batchSize) { munger.transformForDest(input) }
            verify(exactly = batchSize) { buffer.accumulate(Fixtures.mungedRecord) }
            coVerify(exactly = 1) { buffer.flush() }
        }

    @Test
    fun `#finish flushes the buffer`() = runTest {
        loader.finish()
        coVerify(exactly = 1) { buffer.flush() }
    }

    object Fixtures {
        val mungedRecord = mapOf("key" to StringValue("text"))
    }
}
