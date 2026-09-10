/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.config.PipelineInputEvent
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.file.gcs.GcsBlob
import io.airbyte.cdk.load.file.gcs.GcsClient
import io.airbyte.cdk.load.file.object_storage.PartFactory
import io.airbyte.cdk.load.file.object_storage.StreamingUpload
import io.airbyte.cdk.load.message.BatchState
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.PipelineEvent
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.message.StrictPartitionedQueue
import io.airbyte.cdk.load.pipeline.BatchStateUpdate
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.pipeline.FinalOutput
import io.airbyte.cdk.load.pipeline.NoOutput
import io.airbyte.cdk.load.pipeline.OutputPartitioner
import io.airbyte.cdk.load.pipeline.PipelineFlushStrategy
import io.airbyte.cdk.load.pipeline.db.BulkLoaderTableLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectKey
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderFormattedPartPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderLoadedPartPartitioner
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartFormatter
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderPartLoader
import io.airbyte.cdk.load.pipline.object_storage.ObjectLoaderUploadCompleter
import io.airbyte.cdk.load.pipline.object_storage.UploadsInProgress
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointIndex
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.Task
import io.airbyte.cdk.load.task.internal.LoadPipelineStepTaskFactory
import io.airbyte.cdk.load.task.internal.UpdateBatchStateTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.airbyte.cdk.load.write.db.BulkLoaderFactory
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryBulkOneShotUploader
import io.airbyte.integrations.destination.bigquery.write.bulk_loader.BigQueryCopyLoadFixture
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.io.ByteArrayOutputStream
import java.util.UUID
import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.async
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
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.EnumSource

/**
 * Exercises the legacy task loader, not the newer dataflow engine. The formatter is stubbed only to
 * choose a batch boundary; record/checkpoint routing, part uploads, upload completion, load
 * accumulators, task bookkeeping, and checkpoint eligibility use the production implementations. No
 * TCP server is needed: socket events enter at the real bookkeeping router with explicit IDs.
 */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class BigqueryCopyCheckpointTest {
    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `EOF partial batch cannot emit covering state while archive is pending`(
        medium: DataChannelMedium
    ) = runTest {
        val h = Harness(this, medium, finishAtEof = true)
        h.start()
        h.record()
        h.record()
        h.streamCheckpoint(recordCount = 2)
        runCurrent()
        assertFalse(h.fixture().archiveEntered.isCompleted, "Partial batch must wait for finish")
        h.endInput()
        h.fixture().archiveEntered.await()
        h.assertBlocked()

        if (medium == DataChannelMedium.STDIO) {
            assertTrue(h.updates.any { it.state == BatchState.LOADED })
            assertFalse(h.updates.any { it.state == BatchState.COMPLETE })
        }

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
    fun `batch completed by accept is also gated by archive`(medium: DataChannelMedium) = runTest {
        val h = Harness(this, medium, finishAtEof = false)
        h.start()
        h.record()
        h.streamCheckpoint()
        h.fixture().archiveEntered.await()
        h.assertBlocked()
        h.fixture().archiveResult.complete(Unit)
        h.endInput()
        h.awaitPipeline()
        runCurrent()
        assertEquals(1, h.emitted.size)
        assertEquals(1L, h.manager().committedCount(h.checkpointId()).records)
    }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `archive failure during finish cannot emit a covering checkpoint`(
        medium: DataChannelMedium
    ) = runTest {
        val h = Harness(this, medium, finishAtEof = true)
        val failure = IllegalStateException("S3 completion failed")
        h.start()
        h.record()
        h.streamCheckpoint()
        h.endInput()
        h.fixture().archiveEntered.await()
        h.assertBlocked()
        h.fixture().archiveResult.completeExceptionally(failure)
        val actual = h.pipelineResults.last().await().exceptionOrNull()
        assertEquals(failure::class, actual!!::class)
        assertEquals(failure.message, actual.message)
        h.assertBlocked()
        assertFalse(h.manager().isBatchProcessingCompleteForCheckpoints())
        coVerify(exactly = 0) { h.fixture().storage.delete(any<GcsBlob>()) }
    }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `BigQuery failure during finish cannot emit a covering checkpoint`(
        medium: DataChannelMedium
    ) = runTest {
        val h = Harness(this, medium, finishAtEof = true)
        h.fixture().failBigQuery()
        h.start()
        h.record()
        h.streamCheckpoint()
        h.endInput()
        assertNotNull(h.pipelineResults.last().await().exceptionOrNull())
        h.assertBlocked()
        assertFalse(h.fixture().archiveEntered.isCompleted)
        assertFalse(h.manager().isBatchProcessingCompleteForCheckpoints())
    }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `independent stream checkpoint can emit while another stream archive fails`(
        medium: DataChannelMedium
    ) = runTest {
        val h = Harness(this, medium, finishAtEof = false, streamCount = 2)
        h.fixture(0).archiveResult.complete(Unit)
        h.start()
        h.record(stream = 0)
        h.streamCheckpoint(stream = 0)
        h.record(stream = 1)
        h.streamCheckpoint(stream = 1)
        h.fixture(1).archiveEntered.await()
        runCurrent()
        assertEquals(
            listOf("stream-0"),
            h.emitted.map { (it as StreamCheckpoint).checkpoint.unmappedName },
        )
        h.fixture(1).archiveResult.completeExceptionally(IllegalStateException("S3 unavailable"))
        assertNotNull(h.pipelineResults.last().await().exceptionOrNull())
        h.checkpoints.flushReadyCheckpointMessages()
        assertEquals(1, h.emitted.size)
        assertEquals(0L, h.manager(1).committedCount(h.checkpointId()).records)
    }

    @ParameterizedTest
    @EnumSource(DataChannelMedium::class)
    fun `global checkpoint requires archives for all streams`(medium: DataChannelMedium) = runTest {
        val h = Harness(this, medium, finishAtEof = true, streamCount = 2)
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

    @Test
    fun `socket checkpoint arriving before records waits for every partition and source count`() =
        runTest {
            val h = Harness(this, DataChannelMedium.SOCKET, finishAtEof = true, partitions = 2)
            h.start()
            // Unlike STDIO, the control socket may deliver a checkpoint before its records.
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
            assertEquals(1L, h.manager().committedCount(h.checkpointId()).records)
            assertTrue(h.emitted.isEmpty(), "One archived partition cannot cover both records")
            assertFalse(h.manager().isBatchProcessingCompleteForCheckpoints())
            h.fixture(partition = 1).archiveResult.complete(Unit)
            h.awaitPipeline()
            runCurrent()
            assertEquals(1, h.emitted.size)
            assertEquals(2L, h.emitted.single().destinationStats!!.recordCount)
            assertTrue(h.manager().isBatchProcessingCompleteForCheckpoints())
        }

    private class Harness(
        private val scope: TestScope,
        private val medium: DataChannelMedium,
        private val finishAtEof: Boolean,
        streamCount: Int = 1,
        private val partitions: Int = 1,
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
        private val fixtures =
            List(streamCount) { stream ->
                List(partitions) { part ->
                    BigQueryCopyLoadFixture(objectKey = "stream-$stream/part-$part.csv.gz")
                }
            }
        private val input = Array(partitions) { queue<PipelineInputEvent>() }
        private val checkpointQueue = queue<Reserved<CheckpointMessageWrapped>>()
        private val batchQueue = queue<BatchUpdate>()
        val emitted = mutableListOf<CheckpointMessage>()
        val updates = mutableListOf<BatchStateUpdate>()
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
        private val flushStrategy =
            mockk<PipelineFlushStrategy> { every { shouldFlush(any(), any()) } returns false }
        private val taskFactory =
            LoadPipelineStepTaskFactory(
                batchQueue,
                Array(partitions) { input[it].consume() },
                flushStrategy,
            )
        private val bulkFactory = mockk<BulkLoaderFactory<StreamKey, GcsBlob>>()
        private val formatter = mockk<ObjectLoaderPartFormatter<ByteArrayOutputStream>>()
        private val storage = mockk<GcsClient>()
        private val partLoader =
            ObjectLoaderPartLoader(storage, catalog, UploadsInProgress(), mockk(relaxed = true))
        private val completer = ObjectLoaderUploadCompleter<GcsBlob>(bulkFactory)
        val pipelineResults = mutableListOf<Deferred<Result<Unit>>>()

        init {
            every { bulkFactory.stateAfterUpload } returns BatchState.LOADED
            streams.forEachIndexed { streamIndex, stream ->
                val key = StreamKey(stream.mappedDescriptor)
                val nextSocketPartition = AtomicInteger()
                fixtures[streamIndex].forEachIndexed { part, fixture ->
                    every { bulkFactory.create(key, part) } returns fixture.loader
                    coEvery { formatter.start(key, part) } answers
                        {
                            formatterState(stream, fixture)
                        }
                    val upload = mockk<StreamingUpload<GcsBlob>>(relaxed = true)
                    coEvery { upload.complete() } returns fixture.blob
                    coEvery { storage.startStreamingUpload(fixture.blob.key, any()) } returns upload
                }
                coEvery { formatter.startLockFree(key) } answers
                    {
                        formatterState(
                            stream,
                            fixtures[streamIndex][nextSocketPartition.getAndIncrement()],
                        )
                    }
            }
            coEvery { formatter.accept(any(), any()) } answers
                {
                    val state = secondArg<ObjectLoaderPartFormatter.State<ByteArrayOutputStream>>()
                    if (finishAtEof) NoOutput(state) else FinalOutput(finalPart(state))
                }
            coEvery { formatter.finish(any()) } answers { FinalOutput(finalPart(firstArg())) }
        }

        private fun formatterState(stream: DestinationStream, fixture: BigQueryCopyLoadFixture) =
            ObjectLoaderPartFormatter.State<ByteArrayOutputStream>(
                stream,
                mockk(relaxed = true),
                PartFactory(fixture.blob.key, 1L),
            )

        private fun finalPart(state: ObjectLoaderPartFormatter.State<ByteArrayOutputStream>) =
            ObjectLoaderPartFormatter.FormattedPart(
                state.partFactory.nextPart(byteArrayOf(1), true)
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
            // Observe the updates, then let the real task apply counts and decide when to flush.
            val observed =
                object : io.airbyte.cdk.load.message.QueueReader<BatchUpdate> {
                    override fun consume(): Flow<BatchUpdate> =
                        batchQueue.consume().onEach { if (it is BatchStateUpdate) updates.add(it) }

                    override suspend fun poll(): BatchUpdate? = batchQueue.poll()
                }
            scope.backgroundScope.launch {
                UpdateBatchStateTask(observed, sync, checkpoints, mockk(relaxed = true)).execute()
            }
            if (medium == DataChannelMedium.SOCKET) {
                val uploader =
                    BigQueryBulkOneShotUploader(formatter, partLoader, completer, bulkFactory, 2)
                repeat(partitions) { part ->
                    launchTask(
                        taskFactory.createOnlyStep<
                            BigQueryBulkOneShotUploader.BigQueryOneShotUploaderState<
                                ByteArrayOutputStream
                            >,
                            StreamKey,
                            BulkLoaderTableLoader.LoadResult,
                        >(
                            uploader,
                            part,
                            partitions,
                        )
                    )
                }
            } else {
                val parts =
                    partitioned<PipelineEvent<ObjectKey, ObjectLoaderPartFormatter.FormattedPart>>()
                val uploaded =
                    partitioned<
                        PipelineEvent<ObjectKey, ObjectLoaderPartLoader.PartResult<GcsBlob>>
                    >()
                val completed =
                    partitioned<
                        PipelineEvent<StreamKey, ObjectLoaderUploadCompleter.UploadResult<GcsBlob>>
                    >()
                launchTask(
                    taskFactory.createFirstStep(
                        formatter,
                        ObjectLoaderFormattedPartPartitioner(),
                        parts,
                        0,
                        1,
                    )
                ) {
                    parts.close()
                }
                launchTask(
                    taskFactory.createIntermediateStep(
                        partLoader,
                        parts.consume(0),
                        ObjectLoaderLoadedPartPartitioner(),
                        uploaded,
                        0,
                        1,
                        "upload",
                    )
                ) {
                    uploaded.close()
                }
                val partitioner =
                    object :
                        OutputPartitioner<
                            ObjectKey,
                            ObjectLoaderPartLoader.PartResult<GcsBlob>,
                            StreamKey,
                            ObjectLoaderUploadCompleter.UploadResult<GcsBlob>,
                        > {
                        override fun getOutputKey(
                            inputKey: ObjectKey,
                            output: ObjectLoaderUploadCompleter.UploadResult<GcsBlob>,
                        ) = StreamKey(inputKey.stream)

                        override fun getPart(outputKey: StreamKey, inputPart: Int, numParts: Int) =
                            0
                    }
                launchTask(
                    taskFactory.createIntermediateStep(
                        completer,
                        uploaded.consume(0),
                        partitioner,
                        completed,
                        0,
                        1,
                        "complete-upload",
                    )
                ) {
                    completed.close()
                }
                launchTask(
                    taskFactory.createFinalStep(BulkLoaderTableLoader(bulkFactory), completed, 0, 1)
                )
            }
        }

        private fun launchTask(task: Task, closeOutput: suspend () -> Unit = {}) {
            pipelineResults +=
                scope.backgroundScope.async {
                    runCatching { task.execute() }.also { closeOutput() }
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

        suspend fun streamCheckpoint(stream: Int = 0, recordCount: Long = 1) {
            router.handleCheckpoint(
                Reserved<CheckpointMessage>(
                    value =
                        StreamCheckpoint(
                            streams[stream].unmappedNamespace,
                            streams[stream].unmappedName,
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
            checkpoints.flushReadyCheckpointMessages()
            assertTrue(emitted.isEmpty(), "A state covering the unarchived load was emitted")
            assertEquals(0L, manager(stream).committedCount(checkpointId()).records)
        }

        suspend fun awaitPipeline() {
            pipelineResults.forEach { it.await().getOrThrow() }
        }

        private fun <T> queue() = ChannelMessageQueue<T>(Channel(Channel.UNLIMITED))

        private fun <T> partitioned() = StrictPartitionedQueue<T>(arrayOf(queue()))
    }
}
