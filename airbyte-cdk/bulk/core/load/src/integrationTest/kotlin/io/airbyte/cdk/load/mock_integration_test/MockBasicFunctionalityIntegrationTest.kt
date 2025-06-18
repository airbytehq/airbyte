/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.CheckpointMessage.Checkpoint
import io.airbyte.cdk.load.message.InputGlobalCheckpoint
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
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions.assertDoesNotThrow
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
                            streamName = streamName,
                            streamNamespace = streamNamespace,
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
        assertDoesNotThrow {
            runSync(
                updatedConfig,
                stream,
                listOf(
                    // send a state message for a stream that isn't in the catalog.
                    // this should cause the sync to crash.
                    InputGlobalCheckpoint(
                        Jsons.readTree("""{"foo": "bar"}"""),
                        checkpointKeyForMedium(),
                        listOf(
                            Checkpoint(
                                DestinationStream.Descriptor("potato", "tomato"),
                                Jsons.readTree("""{"foo": "bar"}""")
                            )
                        )
                    )
                ),
            )
        }
    }
}
