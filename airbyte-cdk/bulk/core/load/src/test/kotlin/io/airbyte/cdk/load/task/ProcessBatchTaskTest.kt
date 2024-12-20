/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.implementor.DefaultProcessBatchTask
import io.airbyte.cdk.load.write.StreamLoader
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.flow.asFlow
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class ProcessBatchTaskTest {
    private lateinit var syncManager: SyncManager
    private lateinit var streamLoaders: Map<DestinationStream.Descriptor, StreamLoader>
    private lateinit var batchQueue: MultiProducerChannel<BatchEnvelope<*>>
    private lateinit var taskLauncher: DestinationTaskLauncher

    @BeforeEach
    fun setup() {
        val streams =
            (0 until 3).map { DestinationStream.Descriptor(namespace = "test", name = "stream$it") }
        syncManager = mockk(relaxed = true)
        streamLoaders = streams.associateWith { mockk(relaxed = true) }
        streamLoaders.values.forEach {
            coEvery { it.processBatch(any()) } returns SimpleBatch(Batch.State.COMPLETE)
        }
        coEvery { syncManager.getOrAwaitStreamLoader(any()) } answers
            {
                streamLoaders[firstArg()]!!
            }
        batchQueue = mockk(relaxed = true)
        taskLauncher = mockk(relaxed = true)
    }

    @Test
    fun `test each enqueued batch passes through the associated processBatch`() = runTest {
        val task = DefaultProcessBatchTask(syncManager, batchQueue, taskLauncher)
        coEvery { batchQueue.consume() } returns
            streamLoaders.keys
                .map {
                    BatchEnvelope(streamDescriptor = it, batch = SimpleBatch(Batch.State.STAGED))
                }
                .asFlow()

        task.execute()

        streamLoaders.forEach { (descriptor, loader) ->
            coVerify { loader.processBatch(match { it.state == Batch.State.STAGED }) }
            coVerify {
                taskLauncher.handleNewBatch(
                    descriptor,
                    match {
                        it.streamDescriptor == descriptor && it.batch.state == Batch.State.COMPLETE
                    }
                )
            }
        }
    }
}
