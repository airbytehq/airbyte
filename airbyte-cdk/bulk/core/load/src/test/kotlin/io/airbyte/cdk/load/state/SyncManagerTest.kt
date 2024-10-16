/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.state

import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream1
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory.Companion.stream2
import io.airbyte.cdk.load.test.util.CoroutineTestUtils
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import kotlin.test.assertEquals
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

@MicronautTest(
    rebuildContext = true,
    environments =
        [
            "SyncManagerTest",
            "MockDestinationCatalog",
        ]
)
class SyncManagerTest {
    @Inject lateinit var syncManager: SyncManager

    @Test
    fun testGettingNonexistentManagerFails() {
        Assertions.assertThrows(IllegalArgumentException::class.java) {
            syncManager.getStreamManager(DestinationStream.Descriptor("test", "non-existent"))
        }
    }

    // TODO: Don't test getting the stream loader here; A) it's basically just wrapping completable
    //  deferred; B) It should probably move into a writer wrapper.

    @Test
    fun testAwaitAllStreamsCompletedSuccessfully() = runTest {
        val manager1 = syncManager.getStreamManager(stream1.descriptor)
        val manager2 = syncManager.getStreamManager(stream2.descriptor)
        val completionChannel = Channel<Boolean>(Channel.UNLIMITED)

        manager1.markEndOfStream()
        manager2.markEndOfStream()

        launch { completionChannel.send(syncManager.awaitAllStreamsCompletedSuccessfully()) }

        delay(500)
        Assertions.assertTrue(completionChannel.tryReceive().isFailure)
        manager1.markSucceeded()
        delay(500)
        Assertions.assertTrue(completionChannel.tryReceive().isFailure)
        manager2.markSucceeded()
        Assertions.assertTrue(completionChannel.receive())
    }

    @Test
    fun testAwaitAllStreamsCompletedSuccessfullyWithFailure() = runTest {
        val manager1 = syncManager.getStreamManager(stream1.descriptor)
        val manager2 = syncManager.getStreamManager(stream2.descriptor)

        val completionChannel = Channel<Boolean>(Channel.UNLIMITED)

        launch { completionChannel.send(syncManager.awaitAllStreamsCompletedSuccessfully()) }

        manager1.markEndOfStream()
        manager2.markEndOfStream()

        delay(500)
        Assertions.assertTrue(completionChannel.tryReceive().isFailure)
        manager1.markSucceeded()
        delay(500)
        Assertions.assertTrue(completionChannel.tryReceive().isFailure)
        manager2.markFailed(RuntimeException())
        Assertions.assertFalse(completionChannel.receive())
    }

    @Test
    fun testIsActive() = runTest {
        val manager1 = syncManager.getStreamManager(stream1.descriptor)
        val manager2 = syncManager.getStreamManager(stream2.descriptor)

        manager1.markEndOfStream()
        manager2.markEndOfStream()

        Assertions.assertTrue(syncManager.isActive())
        manager1.markSucceeded()
        Assertions.assertTrue(syncManager.isActive())
        manager2.markSucceeded()
        Assertions.assertTrue(syncManager.isActive())
        syncManager.markSucceeded()
        Assertions.assertFalse(syncManager.isActive())
    }

    @Test
    fun testAwaitSyncResult() = runTest {
        val manager1 = syncManager.getStreamManager(stream1.descriptor)
        val manager2 = syncManager.getStreamManager(stream2.descriptor)

        manager1.markEndOfStream()
        manager2.markEndOfStream()

        val completionChannel = Channel<SyncResult>(Channel.UNLIMITED)

        launch { completionChannel.send(syncManager.awaitSyncResult()) }

        CoroutineTestUtils.assertThrows(IllegalStateException::class) {
            syncManager.markSucceeded()
        }
        Assertions.assertTrue(completionChannel.tryReceive().isFailure)

        manager1.markSucceeded()
        CoroutineTestUtils.assertThrows(IllegalStateException::class) {
            syncManager.markSucceeded()
        }
        Assertions.assertTrue(completionChannel.tryReceive().isFailure)

        manager2.markSucceeded()
        Assertions.assertTrue(completionChannel.tryReceive().isFailure)

        syncManager.markSucceeded()
        Assertions.assertEquals(SyncSuccess, completionChannel.receive())
    }

    @Test
    fun testCrashOnNoEndOfStream() = runTest {
        val manager1 = syncManager.getStreamManager(stream1.descriptor)
        manager1.markEndOfStream()
        // This should fail, because stream2 was not marked with end of stream
        val e = assertThrows<IllegalStateException> { syncManager.markInputConsumed() }
        assertEquals(
            // stream1 is fine, so the message only includes stream2
            "Input was fully read, but some streams did not receive a terminal stream status message. This likely indicates an error in the source or platform. Streams without a status message: [test.stream2]",
            e.message
        )
    }
}
