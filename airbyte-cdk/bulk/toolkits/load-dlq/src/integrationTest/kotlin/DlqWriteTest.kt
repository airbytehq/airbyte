/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.integrationTest.DLQ_INTEGRATION_TEST_ENV
import io.airbyte.cdk.load.integrationTest.DLQ_SAMPLE_TEST
import io.airbyte.cdk.load.integrationTest.DLQ_SAMPLE_WITH_EMPTY_LIST_TEST
import io.airbyte.cdk.load.message.CheckpointMessage
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.InputStreamCheckpoint
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.schema.model.ColumnSchema
import io.airbyte.cdk.load.schema.model.StreamTableSchema
import io.airbyte.cdk.load.schema.model.TableName
import io.airbyte.cdk.load.schema.model.TableNames
import io.airbyte.cdk.load.test.mock.MockDestinationDataDumper
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.UncoercedExpectedRecordMapper
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.deserializeToNode
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest.Companion.intType
import io.airbyte.protocol.models.v0.AirbyteMessage
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

@Disabled
open class AbstractDlqWriteTest(
    val configContent: String,
    additionalMicronautEnvs: List<String> = listOf(),
) :
    IntegrationTest(
        dataDumper = MockDestinationDataDumper,
        destinationCleaner = NoopDestinationCleaner,
        recordMangler = UncoercedExpectedRecordMapper,
        nameMapper = NoopNameMapper,
        dataChannelMedium = DataChannelMedium.STDIO,
        dataChannelFormat = DataChannelFormat.JSONL,
        additionalMicronautEnvs = additionalMicronautEnvs,
    ) {
    @Test
    open fun testBasicWrite() {
        val stream =
            DestinationStream(
                unmappedNamespace = randomizedNamespace,
                unmappedName = "test_stream",
                importType = Append,
                schema = ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
                tableSchema =
                    StreamTableSchema(
                        columnSchema =
                            ColumnSchema(
                                inputSchema = mapOf(),
                                inputToFinalColumnNames = mapOf(),
                                finalSchema = mapOf(),
                            ),
                        importType = Append,
                        tableNames = TableNames(finalTableName = TableName("namespace", "test")),
                    ),
            )
        val messages =
            runSync(
                configContents = configContent,
                stream = stream,
                messages =
                    listOf(
                        record(stream, id = 1),
                        record(stream, id = 2),
                        record(stream, id = 3),
                        record(stream, id = 4),
                        record(stream, id = 5),
                        record(stream, id = 6),
                        record(stream, id = 7),
                        record(stream, id = 8),
                        record(stream, id = 9),
                        checkpoint(stream, sourceRecordCount = 9),
                        record(stream, id = 10),
                        record(stream, id = 11),
                        checkpoint(stream, sourceRecordCount = 2),
                    ),
            )

        val stateMessages = messages.filter { it.type == AirbyteMessage.Type.STATE }
        assertAll({
            assertEquals(2, stateMessages.size)

            val checkpoints =
                listOf(
                    StreamCheckpoint(
                            checkpoint =
                                CheckpointMessage.Checkpoint(
                                    unmappedName = stream.unmappedName,
                                    unmappedNamespace = stream.unmappedNamespace,
                                    state = """{"foo": "bar"}""".deserializeToNode(),
                                ),
                            sourceStats =
                                CheckpointMessage.Stats(
                                    recordCount = 9,
                                ),
                            destinationStats =
                                CheckpointMessage.Stats(
                                    recordCount = 5,
                                    rejectedRecordCount = 4,
                                ),
                            serializedSizeBytes = 0L,
                            checkpointKey = null,
                            totalRecords = 5L,
                            totalBytes = 1242,
                            totalRejectedRecords = 4L,
                        )
                        .asProtocolMessage(),
                    StreamCheckpoint(
                            checkpoint =
                                CheckpointMessage.Checkpoint(
                                    unmappedName = stream.unmappedName,
                                    unmappedNamespace = stream.unmappedNamespace,
                                    state = """{"foo": "bar"}""".deserializeToNode(),
                                ),
                            sourceStats =
                                CheckpointMessage.Stats(
                                    recordCount = 2,
                                ),
                            destinationStats =
                                CheckpointMessage.Stats(
                                    recordCount = 2,
                                ),
                            serializedSizeBytes = 0L,
                            checkpointKey = null,
                            totalRecords = 7L,
                            totalBytes = 1520,
                            totalRejectedRecords = 4L,
                        )
                        .asProtocolMessage(),
                )

            val expectedStateMessages =
                checkpoints.map {
                    Jsons.readValue(Jsons.writeValueAsBytes(it), AirbyteMessage::class.java)
                }
            assertEquals(expectedStateMessages, stateMessages)
        },)
    }

    companion object {
        fun record(stream: DestinationStream, id: Int) =
            InputRecord(
                stream = stream,
                data = """{"id": $id}""",
                emittedAtMs = 1234,
                changes = mutableListOf(),
                checkpointId = null,
            )

        fun checkpoint(stream: DestinationStream, sourceRecordCount: Long) =
            InputStreamCheckpoint(
                unmappedName = stream.unmappedName,
                unmappedNamespace = stream.unmappedNamespace,
                blob = """{"foo": "bar"}""",
                sourceRecordCount = sourceRecordCount,
                checkpointKey = null,
            )
    }
}

class NoBucketDlqWriteTest :
    AbstractDlqWriteTest(
        configContent = """{"object_storage_config":{"storage_type":"None"}}""",
        additionalMicronautEnvs = listOf(DLQ_INTEGRATION_TEST_ENV)
    )

class NoBucketConfigDlqWriteTest :
    AbstractDlqWriteTest(
        configContent = """{}""",
        additionalMicronautEnvs = listOf(DLQ_INTEGRATION_TEST_ENV)
    )

class MockBucketDlqFromRecordSampleTest :
    AbstractDlqWriteTest(
        configContent = """{"object_storage_config":{"storage_type":"S3"}}""",
        additionalMicronautEnvs = listOf("MockObjectStorage", DLQ_INTEGRATION_TEST_ENV),
    )

class MockBucketDlqFromRecordSampleWithEmptyListTest :
    AbstractDlqWriteTest(
        configContent = """{"object_storage_config":{"storage_type":"S3"}}""",
        additionalMicronautEnvs =
            listOf("MockObjectStorage", DLQ_INTEGRATION_TEST_ENV, DLQ_SAMPLE_WITH_EMPTY_LIST_TEST),
    )

class MockBucketDlqFromNewRecordsTest :
    AbstractDlqWriteTest(
        configContent = """{"object_storage_config":{"storage_type":"S3"}}""",
        additionalMicronautEnvs =
            listOf("MockObjectStorage", DLQ_INTEGRATION_TEST_ENV, DLQ_SAMPLE_TEST),
    )
