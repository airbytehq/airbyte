/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.DestinationRecord
import io.airbyte.cdk.load.message.DestinationStreamComplete
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NameMapper
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

abstract class BasicFunctionalityIntegrationTest(
    val config: ConfigurationSpecification,
    dataDumper: DestinationDataDumper,
    destinationCleaner: DestinationCleaner,
    recordMangler: ExpectedRecordMapper = NoopExpectedRecordMapper,
    nameMapper: NameMapper = NoopNameMapper,
    /**
     * Whether to actually verify that the connector wrote data to the destination. This should only
     * ever be disabled for test destinations (dev-null, etc.).
     */
    val verifyDataWriting: Boolean = true,
) : IntegrationTest(dataDumper, destinationCleaner, recordMangler, nameMapper) {
    @Test
    open fun testBasicWrite() {
        val stream =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(linkedMapOf("id" to FieldType(IntegerType, nullable = true))),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
            )
        val messages =
            runSync(
                config,
                stream,
                listOf(
                    DestinationRecord(
                        namespace = randomizedNamespace,
                        name = "test_stream",
                        data = """{"id": 5678}""",
                        emittedAtMs = 1234,
                        changes =
                            listOf(
                                DestinationRecord.Change(
                                    field = "foo",
                                    change = AirbyteRecordMessageMetaChange.Change.NULLED,
                                    reason =
                                        AirbyteRecordMessageMetaChange.Reason
                                            .SOURCE_FIELD_SIZE_LIMITATION
                                )
                            )
                    ),
                    StreamCheckpoint(
                        streamName = "test_stream",
                        streamNamespace = randomizedNamespace,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                    )
                )
            )

        val stateMessages = messages.filter { it.type == AirbyteMessage.Type.STATE }
        assertAll(
            {
                assertEquals(
                    1,
                    stateMessages.size,
                    "Expected to receive exactly one state message, got ${stateMessages.size} ($stateMessages)"
                )
                assertEquals(
                    StreamCheckpoint(
                            streamName = "test_stream",
                            streamNamespace = randomizedNamespace,
                            blob = """{"foo": "bar"}""",
                            sourceRecordCount = 1,
                            destinationRecordCount = 1,
                        )
                        .asProtocolMessage(),
                    stateMessages.first()
                )
            },
            {
                if (verifyDataWriting) {
                    dumpAndDiffRecords(
                        config,
                        listOf(
                            OutputRecord(
                                extractedAt = 1234,
                                generationId = 0,
                                data = mapOf("id" to 5678),
                                airbyteMeta =
                                    OutputRecord.Meta(
                                        changes =
                                            listOf(
                                                DestinationRecord.Change(
                                                    field = "foo",
                                                    change =
                                                        AirbyteRecordMessageMetaChange.Change
                                                            .NULLED,
                                                    reason =
                                                        AirbyteRecordMessageMetaChange.Reason
                                                            .SOURCE_FIELD_SIZE_LIMITATION
                                                )
                                            ),
                                        syncId = 42
                                    )
                            )
                        ),
                        stream,
                        primaryKey = listOf(listOf("id")),
                        cursor = null,
                    )
                }
            },
        )
    }

    @Test
    open fun testMidSyncCheckpointingStreamState() =
        runBlocking(Dispatchers.IO) {
            fun makeStream(name: String) =
                DestinationStream(
                    DestinationStream.Descriptor(randomizedNamespace, name),
                    Append,
                    ObjectType(linkedMapOf("id" to FieldType(IntegerType, nullable = true))),
                    generationId = 0,
                    minimumGenerationId = 0,
                    syncId = 42,
                )
            val destination =
                destinationProcessFactory.createDestinationProcess(
                    "write",
                    config,
                    DestinationCatalog(
                            listOf(
                                makeStream("test_stream1"),
                                makeStream("test_stream2"),
                            )
                        )
                        .asProtocolObject(),
                )
            launch { destination.run() }

            // Send one record+state to each stream
            destination.sendMessages(
                DestinationRecord(
                        namespace = randomizedNamespace,
                        name = "test_stream1",
                        data = """{"id": 12}""",
                        emittedAtMs = 1234,
                    )
                    .asProtocolMessage(),
                StreamCheckpoint(
                        streamNamespace = randomizedNamespace,
                        streamName = "test_stream1",
                        blob = """{"foo": "bar1"}""",
                        sourceRecordCount = 1
                    )
                    .asProtocolMessage(),
                DestinationRecord(
                        namespace = randomizedNamespace,
                        name = "test_stream2",
                        data = """{"id": 34}""",
                        emittedAtMs = 1234,
                    )
                    .asProtocolMessage(),
                StreamCheckpoint(
                        streamNamespace = randomizedNamespace,
                        streamName = "test_stream2",
                        blob = """{"foo": "bar2"}""",
                        sourceRecordCount = 1
                    )
                    .asProtocolMessage()
            )
            // Send records to stream1 until we get a state message back.
            // Generally, we expect that that state message will belong to stream1.
            val stateMessages: List<AirbyteStateMessage>
            var i = 0
            while (true) {
                destination.sendMessage(
                    DestinationRecord(
                            namespace = randomizedNamespace,
                            name = "test_stream1",
                            data = """{"id": 56}""",
                            emittedAtMs = 1234,
                        )
                        .asProtocolMessage()
                )
                val returnedMessages = destination.readMessages()
                if (returnedMessages.any { it.type == AirbyteMessage.Type.STATE }) {
                    stateMessages =
                        returnedMessages
                            .filter { it.type == AirbyteMessage.Type.STATE }
                            .map { it.state }
                    break
                }
                i++
            }

            // for each state message, verify that it's a valid state,
            // and that we actually wrote the data
            stateMessages.forEach { stateMessage ->
                val streamName = stateMessage.stream.streamDescriptor.name
                val streamNamespace = stateMessage.stream.streamDescriptor.namespace
                // basic state message checks - this is mostly just exercising the CDK itself,
                // but is cheap and easy to do.
                assertAll(
                    { assertEquals(randomizedNamespace, streamNamespace) },
                    {
                        assertTrue(
                            streamName == "test_stream1" || streamName == "test_stream2",
                            "Expected stream name to be test_stream1 or test_stream2, got $streamName"
                        )
                    },
                    {
                        assertEquals(
                            1.0,
                            stateMessage.destinationStats.recordCount,
                            "Expected destination stats to show 1 record"
                        )
                    },
                    {
                        when (streamName) {
                            "test_stream1" -> {
                                assertEquals(
                                    Jsons.readTree("""{"foo": "bar1"}"""),
                                    stateMessage.stream.streamState,
                                )
                            }
                            "test_stream2" -> {
                                assertEquals(
                                    Jsons.readTree("""{"foo": "bar2"}"""),
                                    stateMessage.stream.streamState
                                )
                            }
                            else ->
                                throw IllegalStateException("Unexpected stream name: $streamName")
                        }
                    }
                )
                if (verifyDataWriting) {
                    val records = dataDumper.dumpRecords(config, makeStream(streamName))
                    val expectedId =
                        when (streamName) {
                            "test_stream1" -> 12
                            "test_stream2" -> 34
                            else ->
                                throw IllegalStateException("Unexpected stream name: $streamName")
                        }
                    val expectedRecord =
                        recordMangler.mapRecord(
                            OutputRecord(
                                extractedAt = 1234,
                                generationId = 0,
                                data = mapOf("id" to expectedId),
                                airbyteMeta = OutputRecord.Meta(changes = listOf(), syncId = 42)
                            )
                        )

                    assertTrue("Expected the first record to be present in the dumped records.") {
                        records.any { actualRecord -> expectedRecord.data == actualRecord.data }
                    }
                }
            }

            destination.sendMessages(
                DestinationStreamComplete(
                        DestinationStream.Descriptor(randomizedNamespace, "test_stream1"),
                        System.currentTimeMillis()
                    )
                    .asProtocolMessage(),
                DestinationStreamComplete(
                        DestinationStream.Descriptor(randomizedNamespace, "test_stream2"),
                        System.currentTimeMillis()
                    )
                    .asProtocolMessage()
            )
            destination.shutdown()
        }
}
