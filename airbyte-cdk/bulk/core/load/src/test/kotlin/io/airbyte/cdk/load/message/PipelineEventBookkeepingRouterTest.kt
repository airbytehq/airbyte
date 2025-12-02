/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.message

import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.pipeline.BatchEndOfStream
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
import io.airbyte.cdk.load.util.deserializeToNode
import io.mockk.*
import java.util.UUID
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class PipelineEventBookkeepingRouterTest {

    private val catalog = mockk<DestinationCatalog>(relaxed = true)
    private val syncManager = mockk<SyncManager>(relaxed = true)
    private val streamManager1 = mockk<StreamManager>(relaxed = true)
    private val streamManager2 = mockk<StreamManager>(relaxed = true)

    private val checkpointQueue =
        mockk<QueueWriter<Reserved<CheckpointMessageWrapped>>>(relaxed = true)
    private val openStreamQueue = mockk<QueueWriter<DestinationStream>>(relaxed = true)
    private val fileTransferQueue = mockk<MessageQueue<FileTransferQueueMessage>>(relaxed = true)
    private val batchStateUpdateQueue = mockk<ChannelMessageQueue<BatchUpdate>>(relaxed = true)

    private val namespaceMapper = NamespaceMapper(NamespaceDefinitionType.SOURCE)

    private val stream1 =
        DestinationStream(
            unmappedNamespace = "ns",
            unmappedName = "s1",
            mockk(),
            mockk(),
            1,
            1,
            1,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                io.airbyte.cdk.load.schema.model.StreamTableSchema(
                    tableNames =
                        io.airbyte.cdk.load.schema.model.TableNames(
                            finalTableName = io.airbyte.cdk.load.schema.model.TableName("ns", "s1")
                        ),
                    columnSchema =
                        io.airbyte.cdk.load.schema.model.ColumnSchema(
                            inputSchema = mapOf(),
                            inputToFinalColumnNames = mapOf(),
                            finalSchema = mapOf(),
                        ),
                    importType = io.airbyte.cdk.load.command.Append,
                )
        )
    private val stream2 =
        DestinationStream(
            unmappedNamespace = "ns",
            unmappedName = "s2",
            mockk(),
            mockk(),
            1,
            1,
            1,
            namespaceMapper = NamespaceMapper(),
            tableSchema =
                io.airbyte.cdk.load.schema.model.StreamTableSchema(
                    tableNames =
                        io.airbyte.cdk.load.schema.model.TableNames(
                            finalTableName = io.airbyte.cdk.load.schema.model.TableName("ns", "s2")
                        ),
                    columnSchema =
                        io.airbyte.cdk.load.schema.model.ColumnSchema(
                            inputSchema = mapOf(),
                            inputToFinalColumnNames = mapOf(),
                            finalSchema = mapOf(),
                        ),
                    importType = io.airbyte.cdk.load.command.Append,
                )
        )

    private fun router(numDataChannels: Int, markEndOfStreamAtEnd: Boolean = false) =
        PipelineEventBookkeepingRouter(
            catalog = catalog,
            syncManager = syncManager,
            checkpointQueue = checkpointQueue,
            openStreamQueue = openStreamQueue,
            fileTransferQueue = fileTransferQueue,
            batchStateUpdateQueue = batchStateUpdateQueue,
            numDataChannels = numDataChannels,
            markEndOfStreamAtEndOfSync = markEndOfStreamAtEnd,
            namespaceMapper = namespaceMapper,
        )

    @BeforeEach
    fun setup() {
        every { catalog.streams } returns listOf(stream1, stream2)

        every { syncManager.getStreamManager(stream1.mappedDescriptor) } returns streamManager1
        every { syncManager.getStreamManager(stream2.mappedDescriptor) } returns streamManager2

        every { streamManager1.incrementReadCount(any()) } returns 1L
        every { streamManager2.incrementReadCount(any()) } returns 1L
        every { streamManager1.incrementByteCount(any(), any()) } returns 0L
        every { streamManager2.incrementByteCount(any(), any()) } returns 0L

        every { streamManager1.readCountForCheckpoint(any()) } returns null
        every { streamManager2.readCountForCheckpoint(any()) } returns null

        coEvery { checkpointQueue.publish(any()) } just Runs
        coEvery { openStreamQueue.publish(any()) } just Runs
        coEvery { fileTransferQueue.publish(any()) } just Runs
        coEvery { batchStateUpdateQueue.publish(any()) } just Runs
    }

    @Test
    fun `record without checkpoint id uses inferred key 1`() = runTest {
        val r = router(1)
        val msg =
            DestinationRecord(
                stream = stream1,
                message = mockk(relaxed = true),
                serializedSizeBytes = 10L,
                checkpointId = null,
                airbyteRawId = UUID.randomUUID()
            )

        val event = r.handleStreamMessage(msg) as PipelineMessage<*, *>

        assertEquals(mapOf(CheckpointId("1") to CheckpointValue(1, 10L)), event.checkpointCounts)
        verify { streamManager1.incrementReadCount(CheckpointId("1")) }
    }

    @Test
    fun `record with explicit checkpoint id does not infer`() = runTest {
        val r = router(1)
        val msg =
            DestinationRecord(
                stream = stream2,
                message = mockk(relaxed = true),
                serializedSizeBytes = 5L,
                checkpointId = CheckpointId("abc"),
                airbyteRawId = UUID.randomUUID()
            )

        val event = r.handleStreamMessage(msg) as PipelineMessage<*, *>

        assertEquals(mapOf(CheckpointId("abc") to CheckpointValue(1, 5L)), event.checkpointCounts)
        verify { streamManager2.incrementReadCount(CheckpointId("abc")) }
    }

    @Test
    fun `first record for unopened stream triggers setup and stream open`() = runTest {
        val r = router(1)
        coEvery { syncManager.awaitSetupComplete() } just Runs
        coEvery { syncManager.getOrAwaitStreamLoader(stream1.mappedDescriptor) } returns mockk()

        r.handleStreamMessage(
            DestinationRecord(
                stream = stream1,
                message = mockk(relaxed = true),
                serializedSizeBytes = 0L,
                checkpointId = null,
                airbyteRawId = UUID.randomUUID()
            ),
        )

        coVerify { syncManager.awaitSetupComplete() }
        coVerify { openStreamQueue.publish(stream1) }
        coVerify { syncManager.getOrAwaitStreamLoader(stream1.mappedDescriptor) }
    }

    @Test
    fun `DestinationRecordStreamComplete marks end immediately when not deferring`() = runTest {
        val r = router(1, markEndOfStreamAtEnd = false)
        r.handleStreamMessage(
            DestinationRecordStreamComplete(stream1, 0L),
        )
        coVerify { streamManager1.markEndOfStream(true) }
    }

    @Test
    fun `legacy file transfer record infers checkpoint id and publishes`() = runTest {
        val r = router(1)
        r.handleStreamMessage(
            DestinationFile(
                stream = stream1,
                emittedAtMs = 0L,
                fileMessage = DestinationFile.AirbyteRecordMessageFile(fileUrl = "s3://x")
            ),
        )

        coVerify {
            fileTransferQueue.publish(
                match<FileTransferQueueRecord> {
                    it.checkpointId == CheckpointId("1") && it.index == 1L
                }
            )
        }
    }

    @Test
    fun `legacy file transfer stream complete publishes EOS and marks`() = runTest {
        val r = router(1)
        r.handleStreamMessage(
            DestinationFileStreamComplete(stream1, 0L),
        )
        coVerify { streamManager1.markEndOfStream(true) }
        coVerify { fileTransferQueue.publish(match { it is FileTransferQueueEndOfStream }) }
    }

    @Test
    fun `stream checkpoint without key infers key and publishes counts`() = runTest {
        val r = router(1)
        every { streamManager1.readCountForCheckpoint(CheckpointId("1")) } returns 7L

        val rm = ReservationManager(1)
        val reserved: Reserved<CheckpointMessage> =
            rm.reserve(
                1,
                StreamCheckpoint(
                    unmappedNamespace = stream1.unmappedNamespace,
                    unmappedName = stream1.unmappedName,
                    blob = """{"a":1}""",
                    sourceRecordCount = 0L,
                    checkpointKey = null
                )
            )

        val slot = slot<Reserved<CheckpointMessageWrapped>>()
        coEvery { checkpointQueue.publish(capture(slot)) } just Runs

        r.handleCheckpoint(reserved)

        val wrapped = slot.captured.value as StreamCheckpointWrapped
        assertEquals(CheckpointId("1"), wrapped.checkpointKey.checkpointId)
        assertEquals(7L, wrapped.checkpoint.destinationStats!!.recordCount)
    }

    @Test
    fun `stream checkpoint with key uses provided key and count`() = runTest {
        val r = router(1)
        every { streamManager1.readCountForCheckpoint(CheckpointId("k")) } returns 3L

        val rm = ReservationManager(1)
        val reserved: Reserved<CheckpointMessage> =
            rm.reserve(
                1,
                StreamCheckpoint(
                    unmappedNamespace = stream1.unmappedNamespace,
                    unmappedName = stream1.unmappedName,
                    blob = """{"b":2}""",
                    sourceRecordCount = 0L,
                    checkpointKey =
                        CheckpointKey(
                            checkpointIndex = CheckpointIndex(1),
                            checkpointId = CheckpointId("k")
                        ),
                    destinationRecordCount = null,
                )
            )

        val slot = slot<Reserved<CheckpointMessageWrapped>>()
        coEvery { checkpointQueue.publish(capture(slot)) } just Runs

        r.handleCheckpoint(reserved)

        val wrapped = slot.captured.value as StreamCheckpointWrapped
        assertEquals(CheckpointId("k"), wrapped.checkpointKey.checkpointId)
        assertEquals(3L, wrapped.checkpoint.destinationStats!!.recordCount)
    }

    @Test
    fun `stream checkpoint with key but missing source stats throws`() = runTest {
        val r = router(1)
        val ck =
            StreamCheckpoint(
                checkpoint =
                    CheckpointMessage.Checkpoint(
                        unmappedNamespace = stream1.unmappedNamespace,
                        unmappedName = stream1.unmappedName,
                        state = """{}""".deserializeToNode(),
                    ),
                sourceStats = null,
                serializedSizeBytes = 0L,
                checkpointKey =
                    CheckpointKey(
                        checkpointIndex = CheckpointIndex(1),
                        checkpointId = CheckpointId("x")
                    ),
            )
        val rm = ReservationManager(1)
        val reserved: Reserved<CheckpointMessage> = rm.reserve(1, ck)
        assertThrows<IllegalStateException> { r.handleCheckpoint(reserved) }
    }

    @Test
    fun `global checkpoint without key infers key and aggregates counts`() = runTest {
        val r = router(1)
        every { streamManager1.readCountForCheckpoint(CheckpointId("1")) } returns 4L
        every { streamManager2.readCountForCheckpoint(CheckpointId("1")) } returns 6L

        val rm = ReservationManager(1)
        val reserved: Reserved<CheckpointMessage> =
            rm.reserve(
                1,
                GlobalCheckpoint(
                    state = """{"g":1}""".deserializeToNode(),
                    sourceStats = null,
                    additionalProperties = emptyMap(),
                    serializedSizeBytes = 0L,
                    checkpointKey = null,
                )
            )
        val slot = slot<Reserved<CheckpointMessageWrapped>>()
        coEvery { checkpointQueue.publish(capture(slot)) } just Runs

        r.handleCheckpoint(reserved)

        val wrapped = slot.captured.value as GlobalCheckpointWrapped
        assertEquals(CheckpointId("1"), wrapped.checkpointKey.checkpointId)
        assertEquals(10L, wrapped.checkpoint.destinationStats!!.recordCount)
    }

    @Test
    fun `global checkpoint with key validates order and aggregates`() = runTest {
        val r = router(1)
        every { streamManager1.readCountForCheckpoint(CheckpointId("g")) } returns 2L
        every { streamManager2.readCountForCheckpoint(CheckpointId("g")) } returns 3L

        val rm = ReservationManager(1)
        val reserved: Reserved<CheckpointMessage> =
            rm.reserve(
                1,
                GlobalCheckpoint(
                    state = null,
                    sourceStats = CheckpointMessage.Stats(0),
                    additionalProperties = emptyMap(),
                    serializedSizeBytes = 0L,
                    checkpointKey =
                        CheckpointKey(
                            checkpointIndex = CheckpointIndex(1),
                            checkpointId = CheckpointId("g")
                        ),
                )
            )
        val slot = slot<Reserved<CheckpointMessageWrapped>>()
        coEvery { checkpointQueue.publish(capture(slot)) } just Runs

        r.handleCheckpoint(reserved)

        val wrapped = slot.captured.value as GlobalCheckpointWrapped
        assertEquals(CheckpointId("g"), wrapped.checkpointKey.checkpointId)
        assertEquals(5L, wrapped.checkpoint.destinationStats!!.recordCount)
    }

    @Test
    fun `global checkpoint missing source stats when key provided throws`() = runTest {
        val r = router(1)
        val ck =
            GlobalCheckpoint(
                state = null,
                sourceStats = null,
                additionalProperties = emptyMap(),
                serializedSizeBytes = 0L,
                checkpointKey =
                    CheckpointKey(
                        checkpointIndex = CheckpointIndex(1),
                        checkpointId = CheckpointId("g")
                    ),
            )
        val rm = ReservationManager(1)
        val reserved: Reserved<CheckpointMessage> = rm.reserve(1, ck)
        assertThrows<IllegalStateException> { r.handleCheckpoint(reserved) }
    }

    @Test
    fun `global snapshot aggregates outer plus inner counts`() = runTest {
        val r = router(1)

        every { streamManager1.readCountForCheckpoint(CheckpointId("snap")) } returns 5L
        every { streamManager2.readCountForCheckpoint(CheckpointId("snap")) } returns 7L
        every { streamManager1.readCountForCheckpoint(CheckpointId("i1")) } returns 2L
        every { streamManager2.readCountForCheckpoint(CheckpointId("i2")) } returns 3L

        val snapshot =
            GlobalSnapshotCheckpoint(
                state = null,
                sourceStats = CheckpointMessage.Stats(0),
                additionalProperties = emptyMap(),
                serializedSizeBytes = 0L,
                checkpointKey =
                    CheckpointKey(
                        checkpointIndex = CheckpointIndex(1),
                        checkpointId = CheckpointId("snap")
                    ),
                streamCheckpoints =
                    mapOf(
                        stream1.mappedDescriptor to
                            CheckpointKey(
                                checkpointIndex = CheckpointIndex(1),
                                checkpointId = CheckpointId("i1")
                            ),
                        stream2.mappedDescriptor to
                            CheckpointKey(
                                checkpointIndex = CheckpointIndex(1),
                                checkpointId = CheckpointId("i2")
                            )
                    )
            )
        val rm = ReservationManager(1)
        val reserved: Reserved<CheckpointMessage> = rm.reserve(1, snapshot)

        val slot = slot<Reserved<CheckpointMessageWrapped>>()
        coEvery { checkpointQueue.publish(capture(slot)) } just Runs

        r.handleCheckpoint(reserved)

        val wrapped = slot.captured.value as GlobalSnapshotCheckpointWrapped
        assertEquals(17L, wrapped.checkpoint.destinationStats!!.recordCount) // (5+2)+(7+3)
        assertEquals(CheckpointId("snap"), wrapped.checkpointKey.checkpointId)
    }

    @Test
    fun `global snapshot without checkpoint key throws`() = runTest {
        val r = router(1)
        val snapshot =
            GlobalSnapshotCheckpoint(
                state = null,
                sourceStats = CheckpointMessage.Stats(0),
                additionalProperties = emptyMap(),
                serializedSizeBytes = 0L,
                checkpointKey = null,
                streamCheckpoints = emptyMap()
            )
        val rm = ReservationManager(1)
        val reserved: Reserved<CheckpointMessage> = rm.reserve(1, snapshot)
        assertThrows<IllegalStateException> { r.handleCheckpoint(reserved) }
    }

    @Test
    fun `close with deferred EOS marks only streams that saw complete`() = runTest {
        val r = router(numDataChannels = 2, markEndOfStreamAtEnd = true)

        r.handleStreamMessage(
            DestinationRecordStreamComplete(stream1, 0L),
        )

        r.close()
        coVerify(exactly = 0) { streamManager1.markEndOfStream(true) }

        r.close()
        coVerify(exactly = 1) { streamManager1.markEndOfStream(true) }
        coVerify(exactly = 0) { streamManager2.markEndOfStream(true) }

        coVerify {
            batchStateUpdateQueue.publish(
                match { it is BatchEndOfStream && it.stream == stream1.mappedDescriptor }
            )
        }
        coVerify {
            batchStateUpdateQueue.publish(
                match { it is BatchEndOfStream && it.stream == stream2.mappedDescriptor }
            )
        }
        coVerify { syncManager.markInputConsumed() }
    }

    @Test
    fun `close without deferred EOS does not re-mark streams`() = runTest {
        val r = router(numDataChannels = 1, markEndOfStreamAtEnd = false)
        r.handleStreamMessage(
            DestinationRecordStreamComplete(stream2, 0L),
        )
        coVerify { streamManager2.markEndOfStream(true) }

        r.close()
        coVerify(exactly = 0) {
            batchStateUpdateQueue.publish(
                match { it is BatchEndOfStream && it.stream == stream2.mappedDescriptor }
            )
        }
    }
}
