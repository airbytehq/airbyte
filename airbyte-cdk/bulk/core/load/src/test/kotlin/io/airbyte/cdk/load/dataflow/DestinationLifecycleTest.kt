/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.config.MemoryAndParallelismConfig
import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.pipeline.PipelineRunner
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class DestinationLifecycleTest {

    private val destinationInitializer: DestinationWriter = mockk(relaxed = true)
    private val destinationCatalog: DestinationCatalog = mockk(relaxed = true)
    private val pipeline: PipelineRunner = mockk(relaxed = true)
    private val completionTracker: StreamCompletionTracker = mockk(relaxed = true)
    private val memoryAndParallelismConfig: MemoryAndParallelismConfig =
        MemoryAndParallelismConfig(maxOpenAggregates = 1, maxBufferedAggregates = 1)

    private val destinationLifecycle =
        DestinationLifecycle(
            destinationInitializer,
            destinationCatalog,
            pipeline,
            completionTracker,
            memoryAndParallelismConfig,
        )

    @Test
    fun `should execute full lifecycle in correct order`() = runTest {
        // Given
        val streamLoader1 = mockk<StreamLoader>(relaxed = true)
        val streamLoader2 = mockk<StreamLoader>(relaxed = true)
        val stream1 = mockk<DestinationStream>(relaxed = true)
        val stream2 = mockk<DestinationStream>(relaxed = true)

        every { completionTracker.allStreamsComplete() } returns true
        every { destinationCatalog.streams } returns listOf(stream1, stream2)
        coEvery { destinationInitializer.createStreamLoader(stream1) } returns streamLoader1
        coEvery { destinationInitializer.createStreamLoader(stream2) } returns streamLoader2

        // When
        destinationLifecycle.run()

        // Then
        coVerify(exactly = 1) { destinationInitializer.setup() }
        coVerify(exactly = 1) { destinationInitializer.createStreamLoader(stream1) }
        coVerify(exactly = 1) { streamLoader1.start() }
        coVerify(exactly = 1) { destinationInitializer.createStreamLoader(stream2) }
        coVerify(exactly = 1) { streamLoader2.start() }
        coVerify(exactly = 1) { pipeline.run() }
        coVerify(exactly = 1) { streamLoader1.teardown(true) }
        coVerify(exactly = 1) { streamLoader2.teardown(true) }
        coVerify(exactly = 1) { destinationInitializer.teardown() }
    }

    @Test
    fun `closes stream loaders exceptionally if all streams not-complete`() = runTest {
        // Given
        val streamLoader1 = mockk<StreamLoader>(relaxed = true)
        val streamLoader2 = mockk<StreamLoader>(relaxed = true)
        val stream1 = mockk<DestinationStream>(relaxed = true)
        val stream2 = mockk<DestinationStream>(relaxed = true)

        every { completionTracker.allStreamsComplete() } returns false
        every { destinationCatalog.streams } returns listOf(stream1, stream2)
        coEvery { destinationInitializer.createStreamLoader(stream1) } returns streamLoader1
        coEvery { destinationInitializer.createStreamLoader(stream2) } returns streamLoader2

        // When
        destinationLifecycle.run()

        // Then
        coVerify(exactly = 1) { destinationInitializer.setup() }
        coVerify(exactly = 1) { destinationInitializer.createStreamLoader(stream1) }
        coVerify(exactly = 1) { streamLoader1.start() }
        coVerify(exactly = 1) { destinationInitializer.createStreamLoader(stream2) }
        coVerify(exactly = 1) { streamLoader2.start() }
        coVerify(exactly = 1) { pipeline.run() }
        coVerify(exactly = 1) { streamLoader1.teardown(false) }
        coVerify(exactly = 1) { streamLoader2.teardown(false) }
        coVerify(exactly = 1) { destinationInitializer.teardown() }
    }
}
