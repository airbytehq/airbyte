/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.CheckpointMessage.Checkpoint
import io.airbyte.cdk.load.message.InputGlobalCheckpoint
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.InputStreamCheckpoint
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.airbyte.cdk.load.test.mock.MockDestinationDataDumper
import io.airbyte.cdk.load.test.mock.MockDestinationSpecification
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.test.util.destination_process.DestinationUncleanExitException
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

class MockBasicFunctionalityIntegrationTest :
    BasicFunctionalityIntegrationTest(
        MockDestinationSpecification.CONFIG,
        MockDestinationSpecification::class.java,
        MockDestinationDataDumper,
        NoopDestinationCleaner,
        UncoercedExpectedRecordMapper,
        NoopNameMapper,
        isStreamSchemaRetroactive = false,
        dedupBehavior = DedupBehavior(),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        preserveUndeclaredFields = true,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior = Untyped,
        additionalMicronautEnvs = listOf(MOCK_TEST_MICRONAUT_ENVIRONMENT),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Test
    override fun testMidSyncCheckpointingStreamState() {
        super.testMidSyncCheckpointingStreamState()
    }

    @Test
    override fun testNamespaces() {
        super.testNamespaces()
    }

    @Test
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    @Test
    override fun testTruncateRefresh() {
        super.testTruncateRefresh()
    }

    @Test
    override fun testInterruptedTruncateWithPriorData() {
        super.testInterruptedTruncateWithPriorData()
    }

    @Test
    override fun resumeAfterCancelledTruncate() {
        super.resumeAfterCancelledTruncate()
    }

    @Test
    override fun testAppend() {
        super.testAppend()
    }

    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Test
    override fun testDedup() {
        super.testDedup()
    }

    @Test
    override fun testDedupWithStringKey() {
        super.testDedupWithStringKey()
    }

    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }

    @Test
    override fun testUnions() {
        super.testUnions()
    }

    @Test
    override fun testBasicTypes() {
        super.testBasicTypes()
    }

    @Test
    fun testCrashInInputLoop() {
        val streamName = "tomato"
        val streamNamespace = "potato"
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
            )
        val e =
            assertThrows<DestinationUncleanExitException> {
                runSync(
                    updatedConfig,
                    stream,
                    listOf(
                        // send a state message for a stream that isn't in the catalog.
                        // this should cause the sync to crash.
                        InputStreamCheckpoint(
                            unmappedName = streamName,
                            unmappedNamespace = streamNamespace,
                            blob = """{"foo": "bar"}""",
                            sourceRecordCount = 1,
                            checkpointKey = checkpointKeyForMedium(),
                        )
                    ),
                )
            }
        assertEquals(
            listOf("Stream not found: Descriptor(namespace=$streamNamespace, name=$streamName)"),
            e.traceMessages.map { it.message },
        )
    }

    @Test
    fun testGlobalStateWithUnknownStreamState() {
        val stream =
            DestinationStream(
                randomizedNamespace,
                "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = namespaceMapperForMedium(),
            )

        val returnedMessages =
            runSync(
                updatedConfig,
                stream,
                listOf(
                    // Send one record, and one global state message
                    InputRecord(stream, """{"id": 42}""", emittedAtMs = 1234),
                    InputGlobalCheckpoint(
                        Jsons.readTree("""{"foo": "bar"}"""),
                        checkpointKeyForMedium(),
                        listOf(
                            // This stream state belongs to the stream in the catalog.
                            Checkpoint(
                                unmappedNamespace = randomizedNamespace,
                                unmappedName = "test_stream",
                                state = Jsons.readTree("""{"abc": "def"}"""),
                            ),
                            // This stream state belongs to a stream that isn't in the catalog.
                            // The sync should still run successfully.
                            Checkpoint(
                                unmappedNamespace = "potato",
                                unmappedName = "tomato",
                                state = Jsons.readTree("""{"ghi": "jkl"}"""),
                            ),
                        ),
                        // Obviously doesn't match reality (we only have one InputRecord).
                        // But the destination isn't responsible for enforcing this, so it's fine.
                        sourceRecordCount = 42,
                    )
                ),
            )

        val returnedStateMessages = returnedMessages.filter { it.type == AirbyteMessage.Type.STATE }
        assertEquals(
            1,
            returnedStateMessages.size,
            "Expected sync to return exactly one state message. Got $returnedStateMessages",
        )
        val returnedStateMessage = returnedStateMessages.first().state
        assertEquals(
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                // Preserve the original source record count
                .withSourceStats(AirbyteStateStats().withRecordCount(42.0))
                // Attach our new destination record count
                .withDestinationStats(AirbyteStateStats().withRecordCount(1.0))
                // attach stats for speed mode
                .withAdditionalProperty("committedBytesCount", 139)
                .withAdditionalProperty("committedRecordsCount", 1)
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(Jsons.readTree("""{"foo": "bar"}"""))
                        .withStreamStates(
                            listOf(
                                AirbyteStreamState()
                                    .withStreamDescriptor(
                                        StreamDescriptor()
                                            .withNamespace(randomizedNamespace)
                                            .withName("test_stream")
                                    )
                                    .withStreamState(Jsons.readTree("""{"abc": "def"}""")),
                                AirbyteStreamState()
                                    .withStreamDescriptor(
                                        StreamDescriptor()
                                            .withNamespace("potato")
                                            .withName("tomato")
                                    )
                                    .withStreamState(Jsons.readTree("""{"ghi": "jkl"}""")),
                            )
                        )
                ),
            returnedStateMessage,
        )
    }
}
