/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationFile
import io.airbyte.cdk.load.message.SimpleBatch
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.write.StreamLoader
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class ProcessFileTaskTest {
    private val stream: DestinationStream.Descriptor =
        DestinationStream.Descriptor("namespace", "name")
    private val taskLauncher: DestinationTaskLauncher = mockk(relaxed = true)
    private val syncManager: SyncManager = mockk(relaxed = true)
    private val file: DestinationFile = mockk(relaxed = true)

    val defaultProcessFileTask = DefaultProcessFileTask(stream, taskLauncher, syncManager, file)

    @Test
    fun `the the file process task execution`() = runTest {
        val mockedStreamLoader = mockk<StreamLoader>(relaxed = true)
        coEvery { syncManager.getOrAwaitStreamLoader(stream) } returns mockedStreamLoader
        val batch = SimpleBatch(Batch.State.COMPLETE)
        coEvery { mockedStreamLoader.processFile(file) } returns batch

        defaultProcessFileTask.execute()

        coVerify { taskLauncher.handleNewBatch(stream, BatchEnvelope(batch)) }
    }
}
