/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointIndex
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.state.CheckpointValue
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.StreamManager
import io.airbyte.cdk.load.state.SyncManager
import io.mockk.coVerify
import io.mockk.every
import io.mockk.impl.annotations.MockK
import io.mockk.mockk
import io.mockk.verify
import java.util.UUID
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class PipelineEventBookkeepingRouterTest {
    @MockK(relaxed = true) lateinit var catalog: DestinationCatalog
    @MockK(relaxed = true) lateinit var syncManager: SyncManager
    @MockK(relaxed = true) lateinit var streamManager: StreamManager
    @MockK(relaxed = true)
    lateinit var checkpointQueue: QueueWriter<Reserved<CheckpointMessageWrapped>>
    @MockK(relaxed = true) lateinit var openStreamQueue: QueueWriter<DestinationStream>
    @MockK(relaxed = true) lateinit var fileTransferQueue: MessageQueue<FileTransferQueueMessage>
    @MockK(relaxed = true) lateinit var batchStateUpdateQueue: ChannelMessageQueue<BatchUpdate>

    private val stream1 =
        DestinationStream(
            unmappedNamespace = "test",
            unmappedName = "stream",
            mockk(),
            mockk(),
            1,
            1,
            1,
            namespaceMapper = NamespaceMapper()
        )

    private fun makeBookkeepingRouter(numDataChannels: Int, markEndOfStreamAtEnd: Boolean = false) =
        PipelineEventBookkeepingRouter(
            catalog,
            syncManager,
            checkpointQueue,
            openStreamQueue,
            fileTransferQueue,
            batchStateUpdateQueue,
            numDataChannels,
            markEndOfStreamAtEnd
        )

    @BeforeEach
    fun setup() {
        every { catalog.streams } returns listOf(stream1)
        every { syncManager.getStreamManager(stream1.descriptor) } returns streamManager
        every { streamManager.incrementReadCount() } returns 1L
    }

    @Test
    fun `router uses inferred checkpoint when checkpoint id not available on record`() = runTest {
        val router =
            makeBookkeepingRouter(
                1,
            )

        every { streamManager.inferNextCheckpointKey() } returns
            CheckpointKey(CheckpointIndex(1), CheckpointId("foo"))

        val event =
            router.handleStreamMessage(
                DestinationRecord(
                    stream = stream1,
                    message = mockk(relaxed = true),
                    serializedSizeBytes = 0L,
                    checkpointId = null,
                    airbyteRawId = UUID.randomUUID()
                ),
                unopenedStreams = mutableSetOf(),
            ) as PipelineMessage

        verify { streamManager.inferNextCheckpointKey() }
        assertEquals(mapOf(CheckpointId("foo") to CheckpointValue(1L, 0L)), event.checkpointCounts)
    }

    @Test
    fun `router does not use inferred checkpoint when checkpoint id is available on record`() =
        runTest {
            val router = makeBookkeepingRouter(1)

            every { streamManager.inferNextCheckpointKey() } returns
                CheckpointKey(CheckpointIndex(1), CheckpointId("foo"))

            val event =
                router.handleStreamMessage(
                    DestinationRecord(
                        stream = stream1,
                        message = mockk(relaxed = true),
                        serializedSizeBytes = 0L,
                        checkpointId = CheckpointId("bar"),
                        airbyteRawId = UUID.randomUUID()
                    ),
                    unopenedStreams = mutableSetOf(),
                ) as PipelineMessage

            verify(exactly = 0) { streamManager.inferNextCheckpointKey() }
            assertEquals(
                mapOf(CheckpointId("bar") to CheckpointValue(1L, 0L)),
                event.checkpointCounts
            )
        }

    @Test
    fun `router infers and marks when checkpoint key is not available on state`() = runTest {
        val router = makeBookkeepingRouter(1)
        val reservationManager = ReservationManager(2)
        val checkpointMessage: CheckpointMessage.Checkpoint = mockk(relaxed = true)

        every { checkpointMessage.stream } returns stream1.descriptor

        every { streamManager.inferNextCheckpointKey() } returns
            CheckpointKey(CheckpointIndex(1), CheckpointId("foo"))
        every { streamManager.markCheckpoint() } returns Pair(0L, 1L)

        router.handleCheckpoint(
            reservationManager.reserve(
                1,
                StreamCheckpoint(checkpointMessage, null, null, emptyMap(), 0, null)
            )
        )
        router.handleCheckpoint(
            reservationManager.reserve(1, GlobalCheckpoint("""{"foo": 1}""", 1L))
        )

        verify(exactly = 2) { streamManager.inferNextCheckpointKey() }
        verify(exactly = 2) { streamManager.markCheckpoint() }
    }

    @Test
    fun `router does not infer or mark when checkpoint key is available on state`() = runTest {
        val router = makeBookkeepingRouter(1)
        val reservationManager = ReservationManager(2)
        val checkpointMessage: CheckpointMessage.Checkpoint = mockk(relaxed = true)

        every { checkpointMessage.stream } returns stream1.descriptor

        every { streamManager.inferNextCheckpointKey() } returns
            CheckpointKey(CheckpointIndex(1), CheckpointId("foo"))
        every { streamManager.markCheckpoint() } returns Pair(0L, 1L)

        val sourceStats = CheckpointMessage.Stats(recordCount = 0)
        router.handleCheckpoint(
            reservationManager.reserve(
                1,
                StreamCheckpoint(
                    checkpointMessage,
                    sourceStats,
                    null,
                    emptyMap(),
                    0,
                    CheckpointKey(CheckpointIndex(2), CheckpointId("bar"))
                )
            )
        )
        val global =
            GlobalCheckpoint(
                null,
                sourceStats,
                null,
                emptyList(),
                emptyMap(),
                null,
                0,
                CheckpointKey(CheckpointIndex(2), CheckpointId("baz"))
            )
        router.handleCheckpoint(reservationManager.reserve(1, global))

        verify(exactly = 0) { streamManager.inferNextCheckpointKey() }
        verify(exactly = 0) { streamManager.markCheckpoint() }
    }

    @Test
    fun `router does not close the stream if forcing close at end of stream`() = runTest {
        val router = makeBookkeepingRouter(2, markEndOfStreamAtEnd = true)

        // Send a record to the first channel
        val eos = DestinationRecordStreamComplete(stream1, 0L)
        router.handleStreamMessage(eos, unopenedStreams = mutableSetOf())

        coVerify(exactly = 0) { streamManager.markEndOfStream(any()) }

        router.handleStreamMessage(eos, unopenedStreams = mutableSetOf())

        coVerify(exactly = 0) { streamManager.markEndOfStream(any()) }

        router.close()

        coVerify(exactly = 0) { streamManager.markEndOfStream(any()) }

        router.close()

        coVerify(exactly = 1) { streamManager.markEndOfStream(any()) }
    }

    @Test
    fun `router throws if stream counts are not present when key and index are provided`() =
        runTest {
            val router = makeBookkeepingRouter(1)
            val reservationManager = ReservationManager(1)

            // Attempt to handle a record with a checkpoint key and index but no stream counts
            assertThrows<IllegalStateException> {
                router.handleCheckpoint(
                    reservationManager.reserve(
                        1,
                        StreamCheckpoint(
                            mockk(relaxed = true),
                            null,
                            null,
                            emptyMap(),
                            0L,
                            CheckpointKey(CheckpointIndex(1), CheckpointId("foo"))
                        )
                    )
                )
            }
        }

    @Test
    fun `router throws if global counts are not present when key and index are provided`() =
        runTest {
            val router = makeBookkeepingRouter(1)
            val reservationManager = ReservationManager(1)

            // Attempt to handle a global checkpoint with a key and index but no counts
            assertThrows<IllegalStateException> {
                router.handleCheckpoint(
                    reservationManager.reserve(
                        1,
                        GlobalCheckpoint(
                            null,
                            null,
                            null,
                            emptyList(),
                            emptyMap(),
                            null,
                            0L,
                            CheckpointKey(CheckpointIndex(1), CheckpointId("foo"))
                        )
                    )
                )
            }
        }
}
