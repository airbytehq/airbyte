/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake.copy

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.write.StreamLoader
import io.mockk.*
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class SnowflakeCopyStreamLoaderTest {
    private val stream = mockk<DestinationStream>()
    private val delegate =
        mockk<StreamLoader>(relaxed = true) {
            every { stream } returns this@SnowflakeCopyStreamLoaderTest.stream
        }
    private val copy = mockk<SnowflakeS3Copy>(relaxed = true)
    private val loader = SnowflakeCopyStreamLoader(delegate, copy)

    @Test
    fun `successful finalization including empty streams publishes completion last`() =
        runBlocking {
            loader.start()
            loader.teardown(true)
            coVerifyOrder {
                delegate.start()
                delegate.teardown(true)
                copy.complete(stream)
            }
        }

    @Test
    fun `failed streams never publish completion`() = runBlocking {
        loader.teardown(false)
        coVerify(exactly = 1) { delegate.teardown(false) }
        coVerify(exactly = 0) { copy.complete(any()) }
    }

    @Test
    fun `failed destination finalization never publishes completion`() = runBlocking {
        coEvery { delegate.teardown(true) } throws IllegalStateException("merge failed")
        assertThrows(IllegalStateException::class.java) { runBlocking { loader.teardown(true) } }
        coVerify(exactly = 0) { copy.complete(any()) }
    }

    @Test
    fun `marker upload failure fails finalization`() = runBlocking {
        coEvery { copy.complete(stream) } throws IllegalStateException("S3 failed")
        assertThrows(IllegalStateException::class.java) { runBlocking { loader.teardown(true) } }
        coVerifyOrder {
            delegate.teardown(true)
            copy.complete(stream)
        }
    }
}
