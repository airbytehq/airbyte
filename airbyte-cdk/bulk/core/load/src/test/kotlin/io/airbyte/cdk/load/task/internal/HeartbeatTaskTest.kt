/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.internal

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.message.PartitionedQueue
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.WithStream
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
    fun <K : WithStream, V> `heartbeat task updates every configured interval`() = runTest {
        val config = mockk<DestinationConfiguration>()
        val recordQueue = mockk<PartitionedQueue<PipelineEvent<K, V>>>()
        val task = HeartbeatTask(config, recordQueue)
        every { config.heartbeatIntervalSeconds } returns 5
        coEvery { recordQueue.broadcast(any()) } returns Unit
        val job = launch { task.execute() }
        delay(10_001L)
        coVerify(atLeast = 2) { recordQueue.broadcast(any()) }
        job.cancel()
    }
}
