/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.task.implementor

import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.google.common.collect.Range
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.MockDestinationCatalogFactory
import io.airbyte.cdk.load.data.IntegerValue
import io.airbyte.cdk.load.message.Batch
import io.airbyte.cdk.load.message.BatchEnvelope
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationRecordAirbyteValue
import io.airbyte.cdk.load.message.MessageQueue
import io.airbyte.cdk.load.message.MultiProducerChannel
import io.airbyte.cdk.load.message.ProtocolMessageDeserializer
import io.airbyte.cdk.load.state.ReservationManager
import io.airbyte.cdk.load.state.SyncManager
import io.airbyte.cdk.load.task.DefaultDestinationTaskLauncher
import io.airbyte.cdk.load.task.internal.SpilledRawMessagesLocalFile
import io.airbyte.cdk.load.util.write
import io.airbyte.cdk.load.write.BatchAccumulator
import io.airbyte.cdk.load.write.StreamLoader
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.coVerifySequence
import io.mockk.mockk
import java.nio.file.Files
import kotlin.io.path.outputStream
import kotlinx.coroutines.flow.asFlow
import kotlinx.coroutines.test.runTest
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

class ProcessRecordsTaskTest {
    private lateinit var config: DestinationConfiguration
    private lateinit var diskManager: ReservationManager
    private lateinit var deserializer: ProtocolMessageDeserializer
    private lateinit var streamLoader: StreamLoader
    private lateinit var batchAccumulator: BatchAccumulator
    private lateinit var inputQueue: MessageQueue<FileAggregateMessage>
    private lateinit var processRecordsTaskFactory: DefaultProcessRecordsTaskFactory
    private lateinit var launcher: DefaultDestinationTaskLauncher<*>
    private lateinit var outputQueue: MultiProducerChannel<BatchEnvelope<*>>
    private lateinit var syncManager: SyncManager

    @BeforeEach
    fun setup() {
        config = mockk(relaxed = true)
        diskManager = mockk(relaxed = true)
        inputQueue = mockk(relaxed = true)
        outputQueue = mockk(relaxed = true)
        syncManager = mockk(relaxed = true)
        streamLoader = mockk(relaxed = true)
        batchAccumulator = mockk(relaxed = true)
        coEvery { config.processEmptyFiles } returns false
        coEvery { syncManager.getOrAwaitStreamLoader(any()) } returns streamLoader
        coEvery { streamLoader.createBatchAccumulator() } returns batchAccumulator
        launcher = mockk(relaxed = true)
        deserializer = mockk(relaxed = true)
        coEvery { deserializer.deserialize(any()) } answers
            {
                DestinationRecord(
                    stream = MockDestinationCatalogFactory.stream1.descriptor,
                    message =
                        AirbyteMessage()
                            .withRecord(
                                AirbyteRecordMessage()
                                    .withEmittedAt(0L)
                                    .withData(
                                        JsonNodeFactory.instance.numberNode(
                                            firstArg<String>().toLong()
                                        )
                                    )
                            ),
                    serialized = "ignored",
                    schema = io.airbyte.cdk.load.data.IntegerType
                )
            }
        processRecordsTaskFactory =
            DefaultProcessRecordsTaskFactory(
                config,
                deserializer,
                syncManager,
                diskManager,
                inputQueue,
                outputQueue,
            )
    }

    class MockBatch(
        override val groupId: String?,
        override val state: Batch.State,
        recordIterator: Iterator<DestinationRecordAirbyteValue>
    ) : Batch {
        val records = recordIterator.asSequence().toList()
    }

    private val recordCount = 1024
    private val serializedRecords = (0 until 1024).map { "$it" }
    private fun makeFile(index: Int): SpilledRawMessagesLocalFile {
        val mockFile = Files.createTempFile("test_$index", ".jsonl")
        mockFile.outputStream().use { outputStream ->
            serializedRecords.map { "$it\n" }.forEach { outputStream.write(it) }
        }
        return SpilledRawMessagesLocalFile(
            localFile = mockFile,
            totalSizeBytes = 999L,
            indexRange = Range.closed(0, recordCount.toLong())
        )
    }

    @Test
    fun `test standard workflow`() = runTest {
        val byteSize = 999L
        val recordCount = 1024L
        val descriptor = MockDestinationCatalogFactory.stream1.descriptor

        // Put three files on the flow.
        val files = (0 until 3).map { makeFile(it) }
        coEvery { inputQueue.consume() } returns
            files.map { FileAggregateMessage(descriptor, it) }.asFlow()

        // Process records returns batches in 3 states.
        coEvery { batchAccumulator.processRecords(any(), any()) } answers
            {
                MockBatch(
                    groupId = null,
                    state = Batch.State.PERSISTED,
                    recordIterator = firstArg()
                )
            } andThenAnswer
            {
                MockBatch(groupId = null, state = Batch.State.COMPLETE, recordIterator = firstArg())
            } andThenAnswer
            {
                MockBatch(
                    groupId = "foo",
                    state = Batch.State.PERSISTED,
                    recordIterator = firstArg()
                )
            }

        // Run the task.
        val task =
            processRecordsTaskFactory.make(
                taskLauncher = launcher,
            )

        task.execute()

        fun batchMatcher(groupId: String?, state: Batch.State): (BatchEnvelope<*>) -> Boolean = {
            it.ranges.encloses(Range.closed(0, recordCount)) &&
                it.streamDescriptor == descriptor &&
                it.batch.groupId == groupId &&
                it.batch.state == state &&
                it.batch is MockBatch &&
                (it.batch as MockBatch)
                    .records
                    .map { record -> (record.data as IntegerValue).value.toString() }
                    .toSet() == serializedRecords.toSet()
        }

        // Verify the batch was *handled* 3 times but *published* ONLY when it is not complete AND
        // group id is null.
        coVerify(exactly = 1) {
            outputQueue.publish(match { batchMatcher(null, Batch.State.PERSISTED)(it) })
        }
        coVerifySequence {
            launcher.handleNewBatch(
                MockDestinationCatalogFactory.stream1.descriptor,
                match { batchMatcher(null, Batch.State.PERSISTED)(it) }
            )
            launcher.handleNewBatch(
                MockDestinationCatalogFactory.stream1.descriptor,
                match { batchMatcher(null, Batch.State.COMPLETE)(it) }
            )
            launcher.handleNewBatch(
                MockDestinationCatalogFactory.stream1.descriptor,
                match { batchMatcher("foo", Batch.State.PERSISTED)(it) }
            )
        }

        files.forEach {
            Assertions.assertFalse(Files.exists(it.localFile), "ensure task deleted file $it")
        }
        coVerify(exactly = 3) { diskManager.release(byteSize) }
    }
}
