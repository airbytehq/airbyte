/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.state.CheckpointManager
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class HeartbeatTaskTest {
    @Test
    fun `heartbeat task updates every configured interval`() = runTest {
        val config = mockk<DestinationConfiguration>()
        val recordQueue = mockk<PartitionedQueue<PipelineInputEvent>>()
        val checkpointManager = mockk<CheckpointManager<*>>()
        val task = HeartbeatTask(config, recordQueue, checkpointManager)
        every { config.heartbeatIntervalSeconds } returns 5
        coEvery { recordQueue.broadcast(any()) } returns Unit
        coEvery { checkpointManager.flushReadyCheckpointMessages() } returns Unit
        val job = launch { task.execute() }
        delay(10_001L)
        coVerify(atLeast = 2) { recordQueue.broadcast(any()) }
        coVerify(atLeast = 2) { checkpointManager.flushReadyCheckpointMessages() }
        job.cancel()
    }
}
