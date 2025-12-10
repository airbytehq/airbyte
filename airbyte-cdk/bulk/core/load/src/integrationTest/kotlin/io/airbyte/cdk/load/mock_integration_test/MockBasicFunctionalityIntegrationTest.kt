/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.mock_integration_test

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.config.NamespaceDefinitionType
import io.airbyte.cdk.load.config.NamespaceMappingConfig
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.CheckpointMessage.Checkpoint
import io.airbyte.cdk.load.message.InputGlobalCheckpoint
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.InputStreamCheckpoint
import io.airbyte.cdk.load.test.mock.MockDestinationBackend.MOCK_TEST_MICRONAUT_ENVIRONMENT
import io.airbyte.cdk.load.test.mock.MockDestinationDataDumper
import io.airbyte.cdk.load.test.mock.MockDestinationSpecification
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.test.util.destination_process.DestinationUncleanExitException
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.protocol.models.v0.AirbyteGlobalState
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStateStats
import io.airbyte.protocol.models.v0.AirbyteStreamState
import io.airbyte.protocol.models.v0.StreamDescriptor
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

abstract class BaseMockBasicFunctionalityIntegrationTest(
    dataChannelMedium: DataChannelMedium,
    dataChannelFormat: DataChannelFormat,
) :
    BasicFunctionalityIntegrationTest(
        MockDestinationSpecification.CONFIG,
        MockDestinationSpecification::class.java,
        MockDestinationDataDumper,
        NoopDestinationCleaner,
        if (dataChannelFormat == DataChannelFormat.PROTOBUF) {
            NoopExpectedRecordMapper
        } else {
            UncoercedExpectedRecordMapper
        },
        NoopNameMapper,
        isStreamSchemaRetroactive = false,
        dedupBehavior = DedupBehavior(),
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior = Untyped,
        additionalMicronautEnvs = listOf(MOCK_TEST_MICRONAUT_ENVIRONMENT),
        dataChannelMedium = dataChannelMedium,
        dataChannelFormat = dataChannelFormat,
        nullEqualsUnset = dataChannelFormat == DataChannelFormat.PROTOBUF,
        unknownTypesBehavior =
            if (dataChannelFormat == DataChannelFormat.PROTOBUF) {
                UnknownTypesBehavior.NULL
            } else {
                UnknownTypesBehavior.PASS_THROUGH
            },
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
    open fun testCrashInInputLoop() {
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
                tableSchema = emptyTableSchema,
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
    open fun testGlobalStateWithUnknownStreamState() {
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
                tableSchema = emptyTableSchema,
            )

        val returnedMessages =
            runSync(
                updatedConfig,
                stream,
                listOf(
                    // Send one record, and one global state message
                    InputRecord(
                        stream,
                        """{"id": 42}""",
                        emittedAtMs = 1234,
                        checkpointId = checkpointKeyForMedium()?.checkpointId
                    ),
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
                        sourceRecordCount = 1,
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
        val expectedStateMessage =
            AirbyteStateMessage()
                .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                .withSourceStats(AirbyteStateStats().withRecordCount(1.0))
                // Attach our new destination record count
                .withDestinationStats(AirbyteStateStats().withRecordCount(1.0))
                // attach stats for speed mode
                .withAdditionalProperty("committedRecordsCount", 1)
                .also { stateMessage ->
                    when (dataChannelMedium) {
                        DataChannelMedium.SOCKET -> {
                            checkpointKeyForMedium()?.let {
                                stateMessage.withAdditionalProperty(
                                    "partition_id",
                                    it.checkpointId.value
                                )
                                stateMessage.withAdditionalProperty("id", it.checkpointIndex.value)
                            }
                            stateMessage.withAdditionalProperty("committedBytesCount", 48)
                        }
                        DataChannelMedium.STDIO -> {
                            stateMessage.withAdditionalProperty("committedBytesCount", 139)
                        }
                    }
                }
                .withGlobal(
                    AirbyteGlobalState()
                        .withSharedState(Jsons.readTree("""{"foo": "bar"}"""))
                        .withStreamStates(
                            listOf(
                                AirbyteStreamState()
                                    .withStreamDescriptor(
                                        StreamDescriptor()
                                            .withNamespace(randomizedNamespace)
                                            .withName("test_stream"),
                                    )
                                    .withStreamState(Jsons.readTree("""{"abc": "def"}"""))
                                    .apply {
                                        if (dataChannelMedium == DataChannelMedium.SOCKET) {
                                            withAdditionalProperty("committedBytesCount", 48)
                                            withAdditionalProperty("committedRecordsCount", 1)
                                        }
                                    },
                                AirbyteStreamState()
                                    .withStreamDescriptor(
                                        StreamDescriptor()
                                            .withNamespace("potato")
                                            .withName("tomato")
                                    )
                                    .withStreamState(Jsons.readTree("""{"ghi": "jkl"}""")),
                            ),
                        ),
                )
        assertEquals(
            expectedStateMessage,
            returnedStateMessage,
        )
    }

    private fun testNamespaceMapping(
        namespaceMappingConfig: NamespaceMappingConfig,
        namespaceValidator: (String?, String?, String, String) -> Unit
    ) {
        assumeTrue(dataChannelMedium == DataChannelMedium.SOCKET)
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream__$randomizedNamespace", // in case namespace == null
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 1,
                minimumGenerationId = 1,
                syncId = 42,
                namespaceMapper =
                    NamespaceMapper(
                        namespaceDefinitionType = namespaceMappingConfig.namespaceDefinitionType,
                        streamPrefix = namespaceMappingConfig.streamPrefix,
                        namespaceFormat = namespaceMappingConfig.namespaceFormat
                    ),
                tableSchema = emptyTableSchema,
            )
        namespaceValidator(
            stream.unmappedNamespace,
            stream.mappedDescriptor.namespace,
            stream.unmappedName,
            stream.mappedDescriptor.name,
        )
        runSync(
            updatedConfig,
            DestinationCatalog(listOf(stream)),
            listOf(
                InputRecord(
                    stream,
                    """{"id": 42}""",
                    emittedAtMs = 1234L,
                    checkpointId = checkpointKeyForMedium()?.checkpointId
                )
            ),
            useFileTransfer = false,
            destinationProcessFactory = destinationProcessFactory,
            namespaceMappingConfig = namespaceMappingConfig
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234L,
                    generationId = 1,
                    data = mapOf("id" to 42),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                )
            ),
            stream,
            primaryKey = listOf(listOf("id")),
            cursor = null,
        )
    }

    @Test
    open fun testNamespaceMappingDestinationNoPrefix() {
        testNamespaceMapping(
            NamespaceMappingConfig(namespaceDefinitionType = NamespaceDefinitionType.DESTINATION)
        ) { _, mappedNamespace, unmappedName, mappedName ->
            // For destination namespace mapping, the namespace should be the unmapped name.
            assertNull(mappedNamespace)
            assertEquals(unmappedName, mappedName)
        }
    }

    @Test
    open fun testNamespaceMappingDestinationWithPrefix() {
        testNamespaceMapping(
            NamespaceMappingConfig(
                namespaceDefinitionType = NamespaceDefinitionType.DESTINATION,
                streamPrefix = "prefix_",
            )
        ) { _, mappedNamespace, unmappedName, mappedName ->
            // For destination namespace mapping, the namespace should be the unmapped name.
            assertNull(mappedNamespace)
            assertEquals("prefix_$unmappedName", mappedName)
        }
    }

    @Test
    open fun testNamespaceMappingSourceWithPrefix() {
        testNamespaceMapping(
            NamespaceMappingConfig(
                namespaceDefinitionType = NamespaceDefinitionType.SOURCE,
                streamPrefix = "prefix_",
            )
        ) { unmappedNamespace, mappedNamespace, unmappedName, mappedName ->
            // For source namespace mapping, the namespace should be the unmapped namespace.
            assertEquals(unmappedNamespace, mappedNamespace)
            assertEquals("prefix_$unmappedName", mappedName)
        }
    }

    @Test
    open fun testNamespaceMappingCustomFormatNoPrefix() {
        testNamespaceMapping(
            NamespaceMappingConfig(
                namespaceDefinitionType = NamespaceDefinitionType.CUSTOM_FORMAT,
                namespaceFormat = "custom_\${SOURCE_NAMESPACE}_namespace",
            )
        ) { _, mappedNamespace, unmappedName, mappedName ->
            // For custom namespace mapping, the namespace should be the custom format.
            assertEquals("custom_${randomizedNamespace}_namespace", mappedNamespace)
            assertEquals(unmappedName, mappedName)
        }
    }

    @Test
    open fun testNamespaceMappingCustomFormatNoMacroWithPrefix() {
        testNamespaceMapping(
            NamespaceMappingConfig(
                namespaceDefinitionType = NamespaceDefinitionType.CUSTOM_FORMAT,
                namespaceFormat = "custom_$randomizedNamespace",
                streamPrefix = "prefix_",
            )
        ) { _, mappedNamespace, unmappedName, mappedName ->
            // For custom namespace mapping, the namespace should be the custom format.
            assertEquals("custom_${randomizedNamespace}", mappedNamespace)
            assertEquals("prefix_$unmappedName", mappedName)
        }
    }
}

// Normal mode
class MockBasicFunctionalityIntegrationTestStdioJsonl :
    BaseMockBasicFunctionalityIntegrationTest(
        DataChannelMedium.STDIO,
        DataChannelFormat.JSONL,
    )

@Disabled
class MockBasicFunctionalityIntegrationTestSocketProtobuf :
    BaseMockBasicFunctionalityIntegrationTest(
        DataChannelMedium.SOCKET,
        DataChannelFormat.PROTOBUF,
    ) {
    // java.time.format.DateTimeParseException: Text 'foo' could not be parsed at index 0
    // expected, protobuf mode assumes valid values.
    @Test
    @Disabled(
        "we need a separate test case that exercises all types, but without bad values - https://github.com/airbytehq/airbyte-internal-issues/issues/13708"
    )
    override fun testBasicTypes() {
        super.testBasicTypes()
    }

    // not suuuper important - this only happens if the source/platform have a bug,
    // and send us a weird state message.
    // probably should fix at some point (probably indicates bad exception handling somewhere),
    // but IMO not critical.
    @Test
    @Disabled("Sockets medium hangs when receiving an unrecognized state message")
    override fun testCrashInInputLoop() {
        super.testCrashInInputLoop()
    }
}

// A few test classes that exist for completeness, but are disabled because we never do these things
// in real syncs.
// They're all broken in weird ways.
@Disabled("not a real mode")
class MockBasicFunctionalityIntegrationTestStdioProtobuf :
    BaseMockBasicFunctionalityIntegrationTest(
        DataChannelMedium.STDIO,
        DataChannelFormat.PROTOBUF,
    )

@Disabled("not a real mode")
class MockBasicFunctionalityIntegrationTestSocketJsonl :
    BaseMockBasicFunctionalityIntegrationTest(
        DataChannelMedium.SOCKET,
        DataChannelFormat.JSONL,
    )

@Disabled("we don't use flatbuffers")
class MockBasicFunctionalityIntegrationTestStdioFlatbuffer :
    BaseMockBasicFunctionalityIntegrationTest(
        DataChannelMedium.STDIO,
        DataChannelFormat.FLATBUFFERS,
    )

@Disabled("we don't use flatbuffers")
class MockBasicFunctionalityIntegrationTestSocketFlatbuffer :
    BaseMockBasicFunctionalityIntegrationTest(
        DataChannelMedium.SOCKET,
        DataChannelFormat.FLATBUFFERS,
    )
