/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.copy

import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.Operation
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.data.ObjectTypeWithEmptySchema
import io.airbyte.cdk.load.file.TimeProvider
import io.airbyte.cdk.load.message.ChannelMessageQueue
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.CheckpointMessageWrapped
import io.airbyte.cdk.load.message.GlobalCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.pipeline.BatchUpdate
import io.airbyte.cdk.load.state.CheckpointId
import io.airbyte.cdk.load.state.CheckpointIndex
import io.airbyte.cdk.load.state.CheckpointKey
import io.airbyte.cdk.load.state.CheckpointManager
import io.airbyte.cdk.load.state.PipelineEventBookkeepingRouter
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.Reserved
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DestinationTaskLauncher
import io.airbyte.cdk.load.task.implementor.FailSyncTask
import io.airbyte.cdk.load.task.implementor.SetupTask
import io.airbyte.cdk.load.task.internal.UpdateCheckpointsTask
import io.airbyte.cdk.load.write.DestinationWriter
import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.integrations.destination.bigquery.spec.BigqueryConfiguration
import io.airbyte.integrations.destination.bigquery.spec.GcsFilePostProcessing
import io.airbyte.integrations.destination.bigquery.spec.GcsStagingConfiguration
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.micronaut.context.ApplicationContext
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.every
import io.mockk.mockk
import java.nio.file.Path
import java.util.UUID
import java.util.stream.Stream
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Deferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.runCurrent
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Assertions.assertInstanceOf
import org.junit.jupiter.api.Assertions.assertNotNull
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.io.TempDir
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

/**
 * A zero-record checkpoint is already data-sufficient before SetupTask completes. The checkpoint
 * consumer must therefore gate the actual emission, including FailSyncTask's final flush. Resolve
 * that consumer through Micronaut so these regressions fail if the connector-local bean is omitted.
 */
@OptIn(kotlinx.coroutines.ExperimentalCoroutinesApi::class)
class BigqueryCopyMetadataCheckpointTest {
    @TempDir lateinit var directory: Path

    @ParameterizedTest
    @MethodSource("checkpointModes")
    fun `zero records cannot emit state until schema and cutoff are durable`(
        medium: DataChannelMedium,
        global: Boolean,
    ) = runTest {
        Fixture(this, medium, global).use { f ->
            f.startSetup()
            f.cutoffEntered.await()
            f.enqueueCheckpoint()
            runCurrent()

            assertEquals(listOf("schema.json"), f.completedMetadata)
            assertTrue(f.streamManager.areRecordsPersistedForCheckpoint(f.key(1).checkpointId))
            assertTrue(
                f.emitted.isEmpty(),
                "Zero-row state escaped while cutoff upload was pending",
            )
            assertEquals(11L, f.reservations.totalBytesReserved)
            assertFalse(f.checkpointTask.isCompleted)
            coVerify(exactly = 0) { f.launcher.handleSetupComplete() }

            f.cutoffResult.complete(Unit)
            f.setupResult.await().getOrThrow()
            f.checkpointTask.await().getOrThrow()
            assertEquals(listOf("schema.json", "generation-cutoff.json"), f.completedMetadata)
            assertEquals(1, f.emitted.size)
            assertEquals(
                if (global) AirbyteStateMessage.AirbyteStateType.GLOBAL
                else AirbyteStateMessage.AirbyteStateType.STREAM,
                f.emitted.single().state.type,
            )
            assertEquals(0L, f.reservations.totalBytesReserved)
            coVerify(exactly = 1) { f.launcher.handleSetupComplete() }
        }
    }

    @ParameterizedTest
    @MethodSource("checkpointModes")
    fun `cutoff failure suppresses and releases zero row states including failed sync flush`(
        medium: DataChannelMedium,
        global: Boolean,
    ) = runTest {
        Fixture(this, medium, global).use { f ->
            f.startSetup()
            f.cutoffEntered.await()
            f.enqueueCheckpoint()
            runCurrent()
            assertTrue(f.emitted.isEmpty(), "Zero-row state escaped before metadata failure")
            assertEquals(11L, f.reservations.totalBytesReserved)

            val failure = IllegalStateException("generation cutoff upload failed")
            f.cutoffResult.completeExceptionally(failure)
            assertNotNull(f.setupResult.await().exceptionOrNull())
            f.checkpointTask.await().getOrThrow()
            assertTrue(f.emitted.isEmpty())
            assertEquals(0L, f.reservations.totalBytesReserved)
            coVerify(exactly = 0) { f.launcher.handleSetupComplete() }

            // FailSyncTask also flushes directly. A failed gate must release rather than throw,
            // otherwise this final flush prevents the task from ever signaling teardown completion.
            val finalState = f.reservations.reserve<CheckpointMessage>(11L, f.message(2))
            if (global) {
                f.checkpoints.addGlobalCheckpoint(f.key(2), finalState)
            } else {
                f.checkpoints.addStreamCheckpoint(f.stream.mappedDescriptor, f.key(2), finalState)
            }
            f.streamManager.markProcessingFailed(failure)
            FailSyncTask(f.launcher, f.writer, failure, f.sync, f.checkpoints).execute()
            assertTrue(f.emitted.isEmpty())
            assertEquals(0L, f.reservations.totalBytesReserved)
            coVerify(exactly = 1) { f.launcher.handleTeardownComplete(false) }
        }
    }

    private inner class Fixture(
        private val scope: TestScope,
        private val medium: DataChannelMedium,
        private val global: Boolean,
    ) : AutoCloseable {
        val stream =
            DestinationStream(
                "namespace",
                "zero-row-refresh",
                Append,
                ObjectTypeWithEmptySchema,
                42L,
                42L,
                101L,
                namespaceMapper = NamespaceMapper(),
            )
        private val catalog = DestinationCatalog(listOf(stream))
        val sync = SyncManager(catalog)
        val streamManager = sync.getStreamManager(stream.mappedDescriptor)
        val reservations = ReservationManager(64L)
        val emitted = mutableListOf<AirbyteMessage>()
        val cutoffEntered = CompletableDeferred<Unit>()
        val cutoffResult = CompletableDeferred<Unit>()
        val completedMetadata = mutableListOf<String>()
        val launcher = mockk<DestinationTaskLauncher>(relaxed = true)
        private val configuration =
            mockk<BigqueryConfiguration> {
                every { loadingMethod } returns
                    GcsStagingConfiguration(mockk(), GcsFilePostProcessing.KEEP)
            }
        private val metadata =
            mockk<BigqueryCopyMetadata> {
                every { descriptor(stream) } returns mapOf("schema_id" to "schema-id")
                every { runPath(stream) } returns "fusion/run"
                every { streamKey(stream) } returns "stream-key"
                every { cutoff(stream) } returns mapOf("minimum_generation_id" to 42L)
                every { serialize(any()) } answers
                    {
                        ObjectMapper().writeValueAsBytes(firstArg<Any>())
                    }
            }
        private val uploader =
            object : ArchiveUploader {
                override suspend fun validateCredentials() = Unit

                override suspend fun upload(
                    path: Path,
                    key: String,
                    contentType: String,
                    metadata: Map<String, String>,
                ) {
                    if (key.endsWith("generation-cutoff.json")) {
                        cutoffEntered.complete(Unit)
                        cutoffResult.await()
                    }
                    completedMetadata.add(key.substringAfterLast('/'))
                }

                override fun close() = Unit
            }
        private val archive =
            EnabledBigqueryS3Copy(
                S3CopyConfiguration(
                    "archive",
                    "us-east-2",
                    "arn:aws:iam::123456789012:role/archive",
                    UUID.randomUUID(),
                    UUID.randomUUID(),
                    UUID.randomUUID(),
                ),
                configuration,
                metadata,
                UUID.randomUUID(),
                { uploader },
                spoolDirectory = directory,
            )
        val writer = BigqueryCopyWriter(mockk<DestinationWriter>(relaxed = true), catalog, archive)
        private val context =
            ApplicationContext.builder()
                .deduceEnvironment(false)
                .environments("connector")
                .properties(
                    mapOf(
                        Operation.PROPERTY to "write",
                        "airbyte.destination.core.data-channel.medium" to medium.name,
                    )
                )
                .build()
        private val checkpointQueue =
            ChannelMessageQueue<Reserved<CheckpointMessageWrapped>>(Channel(Channel.UNLIMITED))
        private val batchQueue = ChannelMessageQueue<BatchUpdate>(Channel(Channel.UNLIMITED))
        val checkpoints: CheckpointManager
        private val router: PipelineEventBookkeepingRouter
        lateinit var setupResult: Deferred<Result<Unit>>
        lateinit var checkpointTask: Deferred<Result<Unit>>

        init {
            val output = mockk<OutputConsumer>(relaxed = true)
            every { output.accept(any<AirbyteMessage>()) } answers
                {
                    emitted.add(firstArg())
                    Unit
                }
            context.registerSingleton(DestinationCatalog::class.java, catalog)
            context.registerSingleton(SyncManager::class.java, sync)
            context.registerSingleton(BigqueryConfiguration::class.java, configuration)
            context.registerSingleton(BigqueryS3Copy::class.java, archive)
            context.registerSingleton(OutputConsumer::class.java, output)
            context.registerSingleton(NamespaceMapper::class.java, NamespaceMapper())
            context.registerSingleton(
                TimeProvider::class.java,
                mockk<TimeProvider> { every { currentTimeMillis() } returns 0L },
            )
            context.start()
            checkpoints = context.getBean(CheckpointManager::class.java)
            assertInstanceOf(BigqueryCopyCheckpointConsumer::class.java, checkpoints.outputConsumer)
            router =
                PipelineEventBookkeepingRouter(
                    catalog,
                    sync,
                    checkpointQueue,
                    mockk(relaxed = true),
                    mockk(relaxed = true),
                    batchQueue,
                    1,
                    medium == DataChannelMedium.SOCKET,
                    NamespaceMapper(),
                )
            coEvery { launcher.handleSetupComplete() } coAnswers { sync.markSetupComplete() }
        }

        fun key(index: Int) =
            CheckpointKey(
                CheckpointIndex(index),
                CheckpointId(
                    if (medium == DataChannelMedium.SOCKET) "source-$index" else index.toString()
                ),
            )

        fun message(index: Int): CheckpointMessage =
            if (global)
                GlobalCheckpoint(
                    state = null,
                    sourceStats = CheckpointMessage.Stats(0L),
                    additionalProperties = emptyMap(),
                    serializedSizeBytes = 0L,
                    checkpointKey = if (medium == DataChannelMedium.SOCKET) key(index) else null,
                )
            else
                StreamCheckpoint(
                    stream.unmappedNamespace,
                    stream.unmappedName,
                    "{}",
                    0L,
                    checkpointKey = if (medium == DataChannelMedium.SOCKET) key(index) else null,
                )

        fun startSetup() {
            setupResult =
                scope.backgroundScope.async(Dispatchers.Default) {
                    runCatching { SetupTask(writer, launcher).execute() }
                }
        }

        suspend fun enqueueCheckpoint() {
            router.handleCheckpoint(reservations.reserve(11L, message(1)))
            checkpointQueue.close()
            checkpointTask =
                scope.backgroundScope.async {
                    runCatching {
                        UpdateCheckpointsTask(sync, checkpoints, checkpointQueue).execute()
                    }
                }
        }

        override fun close() {
            try {
                archive.close()
            } finally {
                context.close()
            }
        }
    }

    companion object {
        @JvmStatic
        fun checkpointModes(): Stream<Arguments> =
            DataChannelMedium.entries
                .flatMap { medium ->
                    listOf(false, true).map { global -> Arguments.of(medium, global) }
                }
                .stream()
    }
}
