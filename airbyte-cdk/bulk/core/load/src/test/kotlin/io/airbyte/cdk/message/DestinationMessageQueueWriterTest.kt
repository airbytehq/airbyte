/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.message

import io.airbyte.cdk.command.DestinationCatalog
import io.airbyte.cdk.command.DestinationStream
import io.airbyte.cdk.command.DestinationStream.Descriptor
import io.airbyte.cdk.state.StateManager
import io.airbyte.cdk.state.StreamManager
import io.airbyte.cdk.state.StreamsManager
import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Prototype
import io.micronaut.context.annotation.Replaces
import io.micronaut.context.annotation.Requires
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import java.util.stream.Stream
import kotlinx.coroutines.channels.Channel
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import org.junit.jupiter.params.provider.ArgumentsSource

@MicronautTest(environments = ["DestinationMessageQueueWriterTest"])
class DestinationMessageQueueWriterTest {
    @Inject lateinit var testContextFactory: TestContextFactory

    @Factory
    class CatalogProvider {
        @Prototype
        @Replaces(DestinationCatalog::class)
        @Requires(env = ["DestinationMessageQueueWriterTest"])
        fun make() =
            DestinationCatalog(
                listOf(
                    DestinationStream(Descriptor("namespace", "stream-1")),
                    DestinationStream(Descriptor("namespace", "stream-2")),
                    DestinationStream(Descriptor("namespace", "stream-3"))
                )
            )
    }

    @Prototype
    @Replaces(StateManager::class)
    @Requires(env = ["DestinationMessageQueueWriterTest"])
    class MockStateManager : StateManager {
        private val streamStateMap =
            mutableMapOf<Pair<DestinationStream, Long>, DestinationStateMessage>()
        private val globalStateQueue =
            mutableListOf<Pair<List<Pair<DestinationStream, Long>>, DestinationStateMessage>>()

        override fun addStreamState(
            stream: DestinationStream,
            index: Long,
            stateMessage: DestinationStateMessage
        ) {
            streamStateMap[Pair(stream, index)] = stateMessage
        }

        override fun addGlobalState(
            streamIndexes: List<Pair<DestinationStream, Long>>,
            stateMessage: DestinationStateMessage
        ) {
            globalStateQueue.add(Pair(streamIndexes, stateMessage))
        }

        override fun flushStates() {
            // Unneeded
        }
    }

    class MockStreamManager : StreamManager {
        override fun countRecordIn(sizeBytes: Long): Long {
            TODO("Not yet implemented")
        }

        override fun markCheckpoint(): Pair<Long, Long> {
            TODO("Not yet implemented")
        }

        override fun <B : Batch> updateBatchState(batch: BatchEnvelope<B>) {
            TODO("Not yet implemented")
        }

        override fun isBatchProcessingComplete(): Boolean {
            TODO("Not yet implemented")
        }

        override fun areRecordsPersistedUntil(index: Long): Boolean {
            TODO("Not yet implemented")
        }

        override fun markClosed() {
            TODO("Not yet implemented")
        }

        override fun streamIsClosed(): Boolean {
            TODO("Not yet implemented")
        }

        override suspend fun awaitStreamClosed() {
            TODO("Not yet implemented")
        }
    }

    @Prototype
    @Replaces(StreamsManager::class)
    @Requires(env = ["DestinationMessageQueueWriterTest"])
    class MockStreamsManager : StreamsManager {
        override fun getManager(stream: DestinationStream): StreamManager {
            TODO()
        }

        override suspend fun awaitAllStreamsComplete() {}
    }

    class MockQueueChannel(
        override val messageQueue: MessageQueue<*, DestinationRecordWrapped>,
        override val channel: Channel<DestinationRecordWrapped>,
    ) : BlockingQueueChannel<DestinationRecordWrapped> {
        override suspend fun send(message: DestinationRecordWrapped) {
            // no-op
        }

        override suspend fun receive(): DestinationRecordWrapped {
            TODO()
        }

        override suspend fun close() {
            TODO("Not yet implemented")
        }

        override suspend fun isClosed(): Boolean {
            TODO("Not yet implemented")
        }
    }

    @Singleton
    @Replaces(QueueChannelFactory::class)
    class MockQueueChannelFactory : QueueChannelFactory<DestinationRecordWrapped> {
        override fun make(
            messageQueue: MessageQueue<*, DestinationRecordWrapped>
        ): QueueChannel<DestinationRecordWrapped> {
            return MockQueueChannel(messageQueue, Channel())
        }
    }

    class MockMessageQueue : MessageQueue<DestinationStream, DestinationRecordWrapped> {
        override suspend fun acquireQueueBytesBlocking(bytes: Long) {
            TODO("Not yet implemented")
        }

        override suspend fun releaseQueueBytes(bytes: Long) {
            TODO("Not yet implemented")
        }

        override suspend fun getChannel(
            key: DestinationStream
        ): QueueChannel<DestinationRecordWrapped> {
            TODO("Not yet implemented")
        }
    }

    @Prototype
    class MockMessageQueueFactory {
        fun make() = MockMessageQueue()
    }

    data class TestContext(
        val writer: DestinationMessageQueueWriter,
        val streamsManager: StreamsManager,
        val stateManager: StateManager
    )

    @Prototype
    class TestContextFactory(
        private val catalog: DestinationCatalog,
        private val messageQueue: MockMessageQueueFactory,
        private val streamsManager: StreamsManager,
        private val stateManager: StateManager
    ) {
        fun make() =
            TestContext(
                writer =
                    DestinationMessageQueueWriter(
                        catalog = catalog,
                        messageQueue = messageQueue.make(),
                        streamsManager = streamsManager,
                        stateManager = stateManager
                    ),
                streamsManager = streamsManager,
                stateManager = stateManager
            )
    }

    data class TestCase(
        val stateIsGlobal: Boolean,
        val nRecords: Int,
        val stateEvery: Int,
        val shuffled: Boolean
    ) {
        fun getRecords(): List<Pair<DestinationMessage, Long>> = TODO()
    }

    /**
     * Scenarios:
     * * nShards: esp 1 versus >1
     * * record versus state versus other
     * * record versus end-of-stream
     * ```
     *     - record routed to shard
     *     - end-of-stream routed to all shards
     * ```
     * * global versus stream state
     * ```
     *     - global index sent to stream manager even when sharded
     * ```
     * * other ignored
     *
     * - new queue writer each time
     * - same catalog is probably fine?
     * - new streams manager and state manager each time
     */
    class DestinationMessageQueueWriterTestArguments : ArgumentsProvider {
        override fun provideArguments(context: ExtensionContext?): Stream<out Arguments> {
            TODO("Not yet implemented")
        }
    }

    @ParameterizedTest
    @ArgumentsSource(DestinationMessageQueueWriterTestArguments::class)
    fun testWritingRecord(testCase: TestCase) = runTest {
        val ctx = testContextFactory.make()
        testCase.getRecords().forEach { (message, size) -> ctx.writer.publish(message, size) }

        // Validate that all global and stream state messages ended up in the state manager
        // with the appropriate indexes

        // Validate that all records were counted and routed to the appropriate shard
    }
}
