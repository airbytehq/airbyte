/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.test.util.CoroutineTestUtils.Companion.assertThrows
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.load.write.StreamLoader
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import kotlinx.coroutines.flow.asFlow
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Test

class OpenStreamTaskTest {
    @MockK(relaxed = true) private lateinit var writer: DestinationWriter
    @MockK(relaxed = true) private lateinit var catalog: DestinationCatalog
    @MockK(relaxed = true) private lateinit var syncManager: SyncManager
    @MockK(relaxed = true) private lateinit var openStreamQueue: MessageQueue<DestinationStream>

    class MyException(message: String) : Exception(message)

    @Test
    fun `test that open stream opens every stream`() = runTest {
        val stream1: DestinationStream = mockk(relaxed = true)
        val stream2: DestinationStream = mockk(relaxed = true)
        val stream3: DestinationStream = mockk(relaxed = true)

        val loader1: StreamLoader = mockk(relaxed = true)
        val loader2: StreamLoader = mockk(relaxed = true)
        val loader3: StreamLoader = mockk(relaxed = true)

        every { catalog.streams } returns listOf(stream1, stream2, stream3)

        coEvery { writer.createStreamLoader(stream1) } returns loader1
        coEvery { writer.createStreamLoader(stream2) } returns loader2
        coEvery { writer.createStreamLoader(stream3) } returns loader3

        coEvery { loader1.start() } returns Unit
        coEvery { loader2.start() } throws MyException("stream2 failed")
        coEvery { loader3.start() } returns Unit

        coEvery { openStreamQueue.consume() } returns
            listOf(stream1, stream2, stream3).asSequence().asFlow()

        coEvery { syncManager.registerStartedStreamLoader(any(), any()) } returns Unit

        val task = DefaultOpenStreamTask(writer, syncManager, openStreamQueue)

        assertThrows(MyException::class) { task.execute() }

        coVerify(exactly = 3) { syncManager.registerStartedStreamLoader(any(), any()) }
    }
}
