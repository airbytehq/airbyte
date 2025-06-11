package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.MockObjectStorageClient
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.file.object_storage.ObjectStorageClient
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.InputStreamCheckpoint
import io.airbyte.cdk.load.message.Meta.Change
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

@Factory
class ShelbyTestingOverrideFactory {
    @Singleton
    fun objectClient(): ObjectStorageClient<*> = MockObjectStorageClient()
}

class ShelbyDataDumper : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        TODO("Not yet implemented")
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        TODO("Not yet implemented")
    }
}

object ShelbyDataCleaner : DestinationCleaner {
    override fun cleanup() {}
}

class ShelbyWriterTest(
) : BasicFunctionalityIntegrationTest(
    configContents = """{
        |"format":{"format_type":"CSV","flattening":"Root level flattening"},
        |"path_pattern":"my-own-crap-path",
        |"file_name_pattern":"{sync_id}-{part_number}-{date}{format_extension}",
        |"s3_path_format":"${'$'}{NAMESPACE}/${'$'}{STREAM_NAME}/",
        |"s3_bucket_name":"yolo",
        |"s3_bucket_path":"destination-shelby",
        |"s3_bucket_region":"us-west-1"
        |}""".trimMargin(),
    configSpecClass = ShelbySpecification::class.java,
    dataDumper = ShelbyDataDumper(),
    destinationCleaner = ShelbyDataCleaner,
    commitDataIncrementally = true,
    allTypesBehavior = Untyped,
    verifyDataWriting = false,
    isStreamSchemaRetroactive = false,
    stringifySchemalessObjects = true,
    schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
    schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
    unionBehavior = UnionBehavior.STRINGIFY,
    preserveUndeclaredFields = true,
    supportFileTransfer = false,
    dedupBehavior = null,
    additionalMicronautEnvs = ShelbyDestination.additionalMicronautEnvs,
) {

    fun record(stream: DestinationStream, id: Int) = InputRecord(
        stream = stream,
        data = """{"id": $id, "text": "let's make this a bigger to have things sliced"}""",
        emittedAtMs = 1234,
        changes = mutableListOf()
    )

    @Test
    fun testActivationWrite() {
        val stream =
            DestinationStream(
//                unmappedNamespace = randomizedNamespace,
                unmappedNamespace = null,
                unmappedName = "test_stream",
                Append,
                ObjectType(linkedMapOf("id" to intType, "text" to stringType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
                namespaceMapper = NamespaceMapper(),
            )
        val messages =
            runSync(
                updatedConfig,
                stream,
                listOf(
                    record(stream, 1),
                    record(stream, 2),
                    record(stream, 3),
                    record(stream, 4),
                    record(stream, 5),
                    record(stream, 6),
                    record(stream, 7),
                    InputStreamCheckpoint(
                        StreamCheckpoint(
                            stream = stream,
                            blob = """{"foo": "bar"}""",
                            sourceRecordCount = 7,
                        )
                    )
                ),
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
                        stream = stream,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 7,
                        destinationRecordCount = 7,
                    )
                        .asProtocolMessage(),
                    stateMessages.first()
                )
            },
            {
                if (verifyDataWriting) {
                    dumpAndDiffRecords(
                        ValidatedJsonUtils.parseOne(configSpecClass, updatedConfig),
                        listOf(
                            OutputRecord(
                                extractedAt = 1234,
                                generationId = 0,
                                data =
                                if (preserveUndeclaredFields) {
                                    mapOf("id" to 5678, "undeclared" to "asdf")
                                } else {
                                    mapOf("id" to 5678)
                                },
                                airbyteMeta =
                                OutputRecord.Meta(
                                    changes =
                                    mutableListOf(
                                        Change(
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
}
