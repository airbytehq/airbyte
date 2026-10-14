/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import com.google.cloud.RetryOption
import com.google.cloud.bigquery.BigQuery
import com.google.cloud.bigquery.BigQueryError
import com.google.cloud.bigquery.FormatOptions
import com.google.cloud.bigquery.Job
import com.google.cloud.bigquery.JobId
import com.google.cloud.bigquery.JobStatistics
import com.google.cloud.bigquery.JobStatus
import com.google.cloud.bigquery.TableDataWriteChannel
import com.google.cloud.bigquery.TableId
import com.google.cloud.bigquery.WriteChannelConfiguration
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.pipeline.BatchStateUpdate
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.DirectLoadPipelineStep
import io.airbyte.cdk.load.pipeline.DirectLoadRecordAccumulator
import io.airbyte.cdk.load.pipeline.PipelineFlushStrategy
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointIndex
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.task.internal.UpdateBatchStateTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.airbyte.cdk.load.write.DirectLoaderFactory
import io.airbyte.integrations.destination.bigquery.write.standard_insert.BigqueryBatchStandardInsertsLoader
import io.airbyte.integrations.destination.bigquery.write.standard_insert.RecordFormatter
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.nio.ByteBuffer
import java.util.UUID
import kotlin.time.Duration.Companion.seconds
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.async
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.launch
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource
import org.junit.jupiter.params.provider.ValueSource

/**
 * The real standard-insert loader drives the legacy direct-load accumulator and checkpoint tasks.
 * Only formatting, BigQuery I/O, and archive I/O are faked. Socket events enter the production
 * bookkeeping router with source checkpoint IDs; these tests do not require a TCP server.
 */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class BigqueryStandardInsertCheckpointTest {
    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `EOF partial batch cannot emit covering state until archive completes`(
        medium: DataChannelMedium
    ) =
        runTest(timeout = 30.seconds) {
            val h = Harness(this, medium)
            h.start()
            h.record()
            h.record()
            h.streamCheckpoint(recordCount = 2)
            runCurrent()
            assertEquals(2L, h.fixture().acceptedRecords)
            assertFalse(
                h.fixture().archiveEntered.isCompleted,
                "Partial batch must wait for finish"
            )
            verify(exactly = 0) { h.fixture().bigQuery.writer(any<JobId>(), any()) }

            h.endInput()
            assertEquals(2L, h.fixture().archiveEntered.await())
            h.assertBlocked()
            assertFalse(h.pipelineResults.single().isCompleted)
            assertFalse(h.updates.any { it.state == BatchState.COMPLETE })

            h.fixture().archiveResult.complete(Unit)
            h.awaitPipeline()
            runCurrent()
            assertEquals(1, h.emitted.size)
            assertEquals(2L, h.emitted.single().destinationStats!!.recordCount)
            assertEquals(2L, h.manager().committedCount(h.checkpointId()).records)
            assertTrue(h.manager().isBatchProcessingCompleteForCheckpoints())
        }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `CDK forced flush waits for archive before acknowledging an open stream`(
        medium: DataChannelMedium
    ) =
        runTest(timeout = 30.seconds) {
            val h = Harness(this, medium, flushAfterRecords = 1)
            h.start()
            h.record()
            h.streamCheckpoint()
            h.fixture().archiveEntered.await()
            h.assertBlocked()
            assertFalse(h.updates.any { it.state == BatchState.COMPLETE })
            h.fixture().archiveResult.complete(Unit)
            runCurrent()
            h.checkpoints.flushReadyCheckpointMessages()
            assertEquals(1, h.emitted.size)
            assertEquals(1L, h.emitted.single().destinationStats!!.recordCount)
            assertEquals(1L, h.manager().committedCount(h.checkpointId()).records)
            assertFalse(h.pipelineResults.single().isCompleted, "Input is still open")
            h.endInput()
            h.awaitPipeline()
        }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `archive failure during EOF finish cannot emit covering state even on failed sync flush`(
        medium: DataChannelMedium
    ) =
        runTest(timeout = 30.seconds) {
            val h = Harness(this, medium)
            h.start()
            h.record()
            h.streamCheckpoint()
            h.endInput()
            h.fixture().archiveEntered.await()
            h.assertBlocked()
            h.fixture().archiveResult.completeExceptionally(IllegalStateException("archive failed"))
            assertNotNull(h.pipelineResults.single().await().exceptionOrNull())
            h.assertBlocked()
            assertFalse(h.updates.any { it.state == BatchState.COMPLETE })
            assertFalse(h.manager().isBatchProcessingCompleteForCheckpoints())
        }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `BigQuery job failure cannot archive or emit covering state`(medium: DataChannelMedium) =
        runTest(timeout = 30.seconds) {
            val h = Harness(this, medium)
            every { h.fixture().job.status.error } returns
                BigQueryError("invalid", "load", "load failed")
            h.start()
            h.record()
            h.streamCheckpoint()
            h.endInput()
            assertNotNull(h.pipelineResults.single().await().exceptionOrNull())
            h.assertBlocked()
            assertFalse(h.fixture().archiveEntered.isCompleted)
            assertFalse(h.updates.any { it.state == BatchState.COMPLETE })
            assertFalse(h.manager().isBatchProcessingCompleteForCheckpoints())
        }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `cancellation during archive completion cannot emit covering state`(
        medium: DataChannelMedium
    ) =
        runTest(timeout = 30.seconds) {
            val h = Harness(this, medium)
            h.start()
            h.record()
            h.streamCheckpoint()
            h.endInput()
            h.fixture().archiveEntered.await()
            h.pipelineResults.single().cancelAndJoin()
            // A late archive result must not revive the cancelled batch or acknowledge its records.
            h.fixture().archiveResult.complete(Unit)
            h.assertBlocked()
            assertFalse(h.updates.any { it.state == BatchState.COMPLETE })
            assertFalse(h.manager().isBatchProcessingCompleteForCheckpoints())
        }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `global checkpoint waits for every stream archive`(medium: DataChannelMedium) =
        runTest(timeout = 30.seconds) {
            val h = Harness(this, medium, streamCount = 2)
            h.fixture(0).archiveResult.complete(Unit)
            h.start()
            h.record(stream = 0)
            h.record(stream = 1)
            h.globalCheckpoint(recordCount = 2)
            h.endInput()
            h.fixture(1).archiveEntered.await()
            h.assertBlocked(stream = 1)
            assertEquals(1L, h.manager(0).committedCount(h.checkpointId()).records)
            h.fixture(1).archiveResult.complete(Unit)
            h.awaitPipeline()
            runCurrent()
            assertEquals(1, h.emitted.size)
            assertTrue(h.emitted.single() is GlobalCheckpoint)
            assertEquals(2L, h.emitted.single().destinationStats!!.recordCount)
        }

    @ParameterizedTest
    @ValueSource(booleans = [false, true])
    fun `socket state arriving before records requires all partition archives`(
        failSecondArchive: Boolean
    ) =
        runTest(timeout = 30.seconds) {
            val h = Harness(this, DataChannelMedium.SOCKET, partitions = 2)
            h.start()
            h.streamCheckpoint(recordCount = 2)
            runCurrent()
            assertTrue(h.emitted.isEmpty())
            h.record(partition = 0)
            h.record(partition = 1)
            h.endInput()
            h.fixture(partition = 0).archiveEntered.await()
            h.fixture(partition = 1).archiveEntered.await()
            h.fixture(partition = 0).archiveResult.complete(Unit)
            h.pipelineResults[0].await().getOrThrow()
            runCurrent()
            h.checkpoints.flushReadyCheckpointMessages()
            assertEquals(1L, h.manager().committedCount(h.checkpointId()).records)
            assertTrue(h.emitted.isEmpty(), "One archived partition cannot cover both records")
            assertFalse(h.manager().isBatchProcessingCompleteForCheckpoints())

            if (failSecondArchive) {
                h.fixture(partition = 1)
                    .archiveResult
                    .completeExceptionally(IllegalStateException("second partition archive failed"))
                assertNotNull(h.pipelineResults[1].await().exceptionOrNull())
                runCurrent()
                h.checkpoints.flushReadyCheckpointMessages()
                assertTrue(h.emitted.isEmpty())
                assertEquals(1L, h.manager().committedCount(h.checkpointId()).records)
                assertFalse(h.manager().isBatchProcessingCompleteForCheckpoints())
            } else {
                h.fixture(partition = 1).archiveResult.complete(Unit)
                h.awaitPipeline()
                runCurrent()
                assertEquals(1, h.emitted.size)
                assertEquals(2L, h.emitted.single().destinationStats!!.recordCount)
                assertEquals(2L, h.manager().committedCount(h.checkpointId()).records)
                assertTrue(h.manager().isBatchProcessingCompleteForCheckpoints())
            }
        }

    private class LoadFixture {
        val bigQuery = mockk<BigQuery>()
        val job = mockk<Job>(relaxed = true)
        private val writer = mockk<TableDataWriteChannel>(relaxed = true)
        private val statistics = mockk<JobStatistics.LoadStatistics>()
        val archiveEntered = CompletableDeferred<Long>()
        val archiveResult = CompletableDeferred<Unit>()
        var acceptedRecords = 0L
            private set

        init {
            every { bigQuery.writer(any<JobId>(), any<WriteChannelConfiguration>()) } returns writer
            every { writer.write(any<ByteBuffer>()) } answers
                {
                    val bytes = firstArg<ByteBuffer>()
                    bytes.remaining().also { bytes.position(bytes.limit()) }
                }
            every { writer.job } returns job
            every { job.waitFor(any<RetryOption>()) } returns job
            every { job.status.error } returns null
            every { job.status.state } returns JobStatus.State.DONE
            every { job.reload() } returns job
            every { job.getStatistics<JobStatistics.LoadStatistics>() } returns statistics
            every { statistics.outputRows } answers { acceptedRecords }
            every { statistics.badRecords } returns 0L
        }

        val loader =
            BigqueryBatchStandardInsertsLoader(
                bigQuery,
                WriteChannelConfiguration.newBuilder(TableId.of("project", "dataset", "table"))
                    .setFormatOptions(FormatOptions.json())
                    .build(),
                JobId.of("project", UUID.randomUUID().toString()),
                object : RecordFormatter {
                    override fun formatRecord(record: DestinationRecordRaw): String {
                        acceptedRecords++
                        return "{\"value\":$acceptedRecords}"
                    }
                },
                archiveBatch =
                    object : StandardInsertArchiveBatch {
                        override fun append(bytes: ByteArray) = Unit

                        override suspend fun complete(loadedRecordCount: Long) {
                            archiveEntered.complete(loadedRecordCount)
                            archiveResult.await()
                        }

                        override fun close() = Unit
                    },
            )
    }

    private class Harness(
        private val scope: TestScope,
        private val medium: DataChannelMedium,
        streamCount: Int = 1,
        private val partitions: Int = 1,
        private val flushAfterRecords: Long? = null,
    ) {
        private val streams =
            List(streamCount) {
                DestinationStream(
                    "namespace",
                    "stream-$it",
                    Append,
                    ObjectTypeWithEmptySchema,
                    42L,
                    0L,
                    101L,
                    namespaceMapper = NamespaceMapper(),
                )
            }
        private val catalog = DestinationCatalog(streams)
        private val sync = SyncManager(catalog)
        private val fixtures = List(streamCount) { List(partitions) { LoadFixture() } }
        private val input = Array(partitions) { queue<PipelineInputEvent>() }
        private val checkpointQueue = queue<Reserved<CheckpointMessageWrapped>>()
        private val batchQueue = queue<BatchUpdate>()
        val emitted = mutableListOf<CheckpointMessage>()
        val updates = mutableListOf<BatchStateUpdate>()
        val pipelineResults = mutableListOf<Deferred<Result<Unit>>>()
        val checkpoints =
            CheckpointManager(
                catalog,
                sync,
                { reservation, _, _, _ ->
                    emitted.add(reservation.value)
                    Unit
                },
                mockk { every { currentTimeMillis() } returns 0L },
                medium == DataChannelMedium.SOCKET,
                NamespaceMapper(),
            )
        private val router =
            PipelineEventBookkeepingRouter(
                catalog,
                sync,
                checkpointQueue,
                mockk(relaxed = true),
                mockk(relaxed = true),
                batchQueue,
                partitions,
                medium == DataChannelMedium.SOCKET,
                NamespaceMapper(),
            )

        suspend fun start() {
            sync.markSetupComplete()
            streams.forEach {
                sync.registerStartedStreamLoader(
                    it.mappedDescriptor,
                    Result.success(mockk(relaxed = true)),
                )
            }
            scope.backgroundScope.launch {
                UpdateCheckpointsTask(sync, checkpoints, checkpointQueue).execute()
            }
            val observed =
                object : io.airbyte.cdk.load.message.QueueReader<BatchUpdate> {
                    override fun consume(): Flow<BatchUpdate> =
                        batchQueue.consume().onEach { if (it is BatchStateUpdate) updates.add(it) }

                    override suspend fun poll(): BatchUpdate? = batchQueue.poll()
                }
            scope.backgroundScope.launch {
                UpdateBatchStateTask(observed, sync, checkpoints, mockk(relaxed = true)).execute()
            }
            val factory =
                object : DirectLoaderFactory<BigqueryBatchStandardInsertsLoader> {
                    override fun create(
                        streamDescriptor: DestinationStream.Descriptor,
                        part: Int,
                    ): BigqueryBatchStandardInsertsLoader {
                        val stream =
                            streams.indexOfFirst { it.mappedDescriptor == streamDescriptor }
                        return fixtures[stream][part].loader
                    }
                }
            val taskFactory =
                LoadPipelineStepTaskFactory(
                    batchQueue,
                    Array(partitions) { input[it].consume() },
                    // Normally finish at EOS; force an earlier boundary for the flush test.
                    object : PipelineFlushStrategy {
                        override fun shouldFlush(inputCount: Long, dataAgeMs: Long): Boolean =
                            flushAfterRecords?.let { inputCount >= it } ?: false
                    },
                )
            val step =
                DirectLoadPipelineStep(
                    factory,
                    DirectLoadRecordAccumulator<BigqueryBatchStandardInsertsLoader, StreamKey>(
                        factory
                    ),
                    taskFactory,
                    partitions,
                )
            repeat(partitions) { part ->
                pipelineResults +=
                    scope.backgroundScope.async {
                        runCatching { step.taskForPartition(part).execute() }
                    }
            }
        }

        fun fixture(stream: Int = 0, partition: Int = 0) = fixtures[stream][partition]

        fun manager(stream: Int = 0) = sync.getStreamManager(streams[stream].mappedDescriptor)

        fun checkpointId() =
            CheckpointId(if (medium == DataChannelMedium.SOCKET) "source-checkpoint" else "1")

        private fun checkpointKey() =
            if (medium == DataChannelMedium.SOCKET)
                CheckpointKey(CheckpointIndex(1), checkpointId())
            else null

        suspend fun record(stream: Int = 0, partition: Int = 0) {
            input[partition].publish(
                router.handleStreamMessage(
                    DestinationRecord(
                        stream = streams[stream],
                        message = mockk(relaxed = true),
                        serializedSizeBytes = 10L,
                        checkpointId = checkpointKey()?.checkpointId,
                        airbyteRawId = UUID.randomUUID(),
                    )
                )
            )
        }

        suspend fun streamCheckpoint(recordCount: Long = 1) {
            router.handleCheckpoint(
                Reserved<CheckpointMessage>(
                    value =
                        StreamCheckpoint(
                            streams[0].unmappedNamespace,
                            streams[0].unmappedName,
                            "{}",
                            recordCount,
                            checkpointKey = checkpointKey(),
                        )
                )
            )
        }

        suspend fun globalCheckpoint(recordCount: Long) {
            router.handleCheckpoint(
                Reserved<CheckpointMessage>(
                    value =
                        GlobalCheckpoint(
                            state = null,
                            sourceStats = CheckpointMessage.Stats(recordCount),
                            additionalProperties = emptyMap(),
                            serializedSizeBytes = 0L,
                            checkpointKey = checkpointKey(),
                        )
                )
            )
        }

        suspend fun endInput() {
            repeat(partitions) { partition ->
                streams.forEach { stream ->
                    input[partition].publish(
                        router.handleStreamMessage(DestinationRecordStreamComplete(stream, 0L))
                    )
                }
                input[partition].close()
                router.close()
            }
        }

        suspend fun assertBlocked(stream: Int = 0) {
            scope.runCurrent()
            // FailSyncTask also flushes eligible checkpoints: failure must not make this one ready.
            checkpoints.flushReadyCheckpointMessages()
            assertTrue(emitted.isEmpty(), "A state covering the unarchived load was emitted")
            assertEquals(0L, manager(stream).committedCount(checkpointId()).records)
        }

        suspend fun awaitPipeline() {
            pipelineResults.forEach { it.await().getOrThrow() }
        }

        private fun <T> queue() = ChannelMessageQueue<T>(Channel(Channel.UNLIMITED))
    }
}
