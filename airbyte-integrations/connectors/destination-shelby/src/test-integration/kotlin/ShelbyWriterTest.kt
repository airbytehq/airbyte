import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.InputStreamCheckpoint
import io.airbyte.cdk.load.message.Meta.Change
import io.airbyte.cdk.load.message.StreamCheckpoint
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.integrations.destination.shelby.ShelbyDestination
import io.airbyte.integrations.destination.shelby.ShelbySpecification
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

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
    configContents = "{}",
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

    fun record(id: Int) = InputRecord(
        namespace = randomizedNamespace,
        name = "test_stream",
        data = """{"id": $id, "text": "let's make this a bigger to have things sliced"}""",
        emittedAtMs = 1234,
        changes = mutableListOf()
    )

    @Test
    fun testActivationWrite() {
        val stream =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(linkedMapOf("id" to intType, "text" to stringType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
            )
        val messages =
            runSync(
                updatedConfig,
                stream,
                listOf(
                    record(1),
                    record(2),
                    record(3),
                    record(4),
                    record(5),
                    record(6),
                    record(7),
                    InputStreamCheckpoint(
                        streamName = "test_stream",
                        streamNamespace = randomizedNamespace,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 7,
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
                        streamName = "test_stream",
                        streamNamespace = randomizedNamespace,
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
