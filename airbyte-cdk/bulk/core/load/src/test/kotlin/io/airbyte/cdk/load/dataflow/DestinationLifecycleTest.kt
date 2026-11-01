/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.dataflow

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.dataflow.finalization.StreamCompletionTracker
import io.airbyte.cdk.load.dataflow.pipeline.PipelineRunner
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class DestinationLifecycleTest {

    private val destinationInitializer: DestinationWriter = mockk(relaxed = true)
    private val destinationCatalog: DestinationCatalog = mockk(relaxed = true)
    private val pipeline: PipelineRunner = mockk(relaxed = true)
    private val completionTracker: StreamCompletionTracker = mockk(relaxed = true)
    private val streamInitDispatcher = Dispatchers.Default
    private val streamFinalizeDispatcher = Dispatchers.Default

    private val destinationLifecycle =
        DestinationLifecycle(
            destinationInitializer,
            destinationCatalog,
            pipeline,
            completionTracker,
            streamInitDispatcher,
            streamFinalizeDispatcher,
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

    @Test
    fun `tears down opted-in loaders based on stream completion`() = runTest {
        // Given
        val completedStreamLoader = mockk<StreamLoader>(relaxed = true)
        val incompleteStreamLoader = mockk<StreamLoader>(relaxed = true)
        val nonOptedInStreamLoader = mockk<StreamLoader>(relaxed = true)
        val completedStream = mockk<DestinationStream>(relaxed = true)
        val incompleteStream = mockk<DestinationStream>(relaxed = true)
        val nonOptedInStream = mockk<DestinationStream>(relaxed = true)
        val completedDescriptor = DestinationStream.Descriptor("namespace", "completed")
        val incompleteDescriptor = DestinationStream.Descriptor("namespace", "incomplete")
        val nonOptedInDescriptor = DestinationStream.Descriptor("namespace", "non_opted_in")

        every { completedStream.mappedDescriptor } returns completedDescriptor
        every { incompleteStream.mappedDescriptor } returns incompleteDescriptor
        every { nonOptedInStream.mappedDescriptor } returns nonOptedInDescriptor
        every { completedStreamLoader.stream } returns completedStream
        every { incompleteStreamLoader.stream } returns incompleteStream
        every { nonOptedInStreamLoader.stream } returns nonOptedInStream
        every { completedStreamLoader.teardownOnStreamCompletion } returns true
        every { incompleteStreamLoader.teardownOnStreamCompletion } returns true
        every { nonOptedInStreamLoader.teardownOnStreamCompletion } returns false
        every { completionTracker.allStreamsComplete() } returns false
        every { completionTracker.isStreamComplete(completedDescriptor) } returns true
        every { completionTracker.isStreamComplete(incompleteDescriptor) } returns false
        every { completionTracker.isStreamComplete(nonOptedInDescriptor) } returns true
        every { destinationCatalog.streams } returns
            listOf(completedStream, incompleteStream, nonOptedInStream)
        coEvery { destinationInitializer.createStreamLoader(completedStream) } returns
            completedStreamLoader
        coEvery { destinationInitializer.createStreamLoader(incompleteStream) } returns
            incompleteStreamLoader
        coEvery { destinationInitializer.createStreamLoader(nonOptedInStream) } returns
            nonOptedInStreamLoader

        // When
        destinationLifecycle.run()

        // Then
        coVerify(exactly = 1) { completedStreamLoader.teardown(true) }
        coVerify(exactly = 1) { incompleteStreamLoader.teardown(false) }
        coVerify(exactly = 1) { nonOptedInStreamLoader.teardown(false) }
    }
}
