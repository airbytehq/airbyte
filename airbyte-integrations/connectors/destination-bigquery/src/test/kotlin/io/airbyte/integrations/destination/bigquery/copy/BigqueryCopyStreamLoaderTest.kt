/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.load.command.*
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.state.StreamProcessingFailed
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.implementor.CloseStreamTask
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.mockk.*
import kotlinx.coroutines.*
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class BigqueryCopyStreamLoaderTest {
    private val stream =
        DestinationStream(
            "ns",
            "empty",
            Append,
            ObjectTypeWithEmptySchema,
            9L,
            9L,
            12345L,
            namespaceMapper = NamespaceMapper()
        )
    private val catalog = DestinationCatalog(listOf(stream))
    private val delegate =
        mockk<StreamLoader>(relaxed = true) {
            every { stream } returns this@BigqueryCopyStreamLoaderTest.stream
        }
    private val archive = mockk<BigqueryS3Copy>(relaxed = true)
    private val sync = SyncManager(catalog)
    private val writer =
        BigqueryCopyWriter(
            mockk<DestinationWriter> { every { createStreamLoader(stream) } returns delegate },
            catalog,
            archive,
            sync,
        )
    private val loader =
        writer.createStreamLoader(stream).also {
            sync.registerStartedStreamLoader(stream.mappedDescriptor, Result.success(it))
        }
    private val launcher = mockk<DestinationTaskLauncher>(relaxed = true)

    @Test
    fun `actual close task waits for empty stream marker before reporting success`() = runBlocking {
        sync.getStreamManager(stream.mappedDescriptor).markEndOfStream(true)
        val entered = CompletableDeferred<Unit>()
        val durable = CompletableDeferred<Unit>()
        coEvery { archive.complete(stream) } coAnswers
            {
                entered.complete(Unit)
                durable.await()
            }
        val task = async { CloseStreamTask(sync, stream.mappedDescriptor, launcher).execute() }
        entered.await()
        assertFalse(task.isCompleted)
        coVerify(exactly = 1) { delegate.close(false, null) }
        coVerify(exactly = 0) { launcher.handleStreamClosed() }
        durable.complete(Unit)
        task.await()
        coVerifyOrder {
            delegate.close(false, null)
            archive.complete(stream)
            launcher.handleStreamClosed()
        }
    }

    @Test
    fun `marker failure prevents actual close task from reporting success`() = runBlocking {
        sync.getStreamManager(stream.mappedDescriptor).markEndOfStream(true)
        coEvery { archive.complete(stream) } throws IllegalStateException("S3 failed")
        assertThrows(IllegalStateException::class.java) {
            runBlocking { CloseStreamTask(sync, stream.mappedDescriptor, launcher).execute() }
        }
        coVerify(exactly = 0) { launcher.handleStreamClosed() }
    }

    @Test
    fun `incomplete EOF closes without publishing a completion marker`() = runBlocking {
        sync.getStreamManager(stream.mappedDescriptor).markEndOfStream(false)
        CloseStreamTask(sync, stream.mappedDescriptor, launcher).execute()
        coVerify(exactly = 1) { delegate.close(false, null) }
        coVerify(exactly = 0) { archive.complete(any()) }
    }

    @Test
    fun `failed streams never emit a completion marker`() = runBlocking {
        val failure = StreamProcessingFailed(IllegalStateException("load failed"))
        loader.close(true, failure)
        coVerify(exactly = 1) { delegate.close(true, failure) }
        coVerify(exactly = 0) { archive.complete(any()) }
    }

    @Test
    fun `failed destination finalization never emits a completion marker`() = runBlocking {
        coEvery { delegate.close(any(), any()) } throws IllegalStateException("merge failed")
        assertThrows(IllegalStateException::class.java) { runBlocking { loader.close(true) } }
        coVerify(exactly = 0) { archive.complete(any()) }
    }

    @Test
    fun `teardown entry point preserves start and completion behavior`() = runBlocking {
        sync.getStreamManager(stream.mappedDescriptor).markEndOfStream(true)
        loader.start()
        loader.teardown(true)
        coVerifyOrder {
            delegate.start()
            delegate.close(true, null)
            archive.complete(stream)
        }
    }
}
