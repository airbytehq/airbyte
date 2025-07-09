/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.message.InputStreamCheckpoint
import io.airbyte.cdk.load.message.Meta.Change
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.Untyped
import io.airbyte.integrations.destination.customerio.CustomerIoSpecification
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

class CustomerIoDataDumper : DestinationDataDumper {
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

object CustomerIoDataCleaner : DestinationCleaner {
    override fun cleanup() {}
}

class CustomerIoWriterTest :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Path.of("secrets/config.json")),
        configSpecClass = CustomerIoSpecification::class.java,
        dataDumper = CustomerIoDataDumper(),
        destinationCleaner = CustomerIoDataCleaner,
        commitDataIncrementally = true,
        allTypesBehavior = Untyped,
        verifyDataWriting = false,
        isStreamSchemaRetroactive = false,
        dedupBehavior = null,
        stringifySchemalessObjects = true,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        unionBehavior = UnionBehavior.STRINGIFY,
        supportFileTransfer = false,
    ) {
    private val personEventStream: DestinationStream =
        DestinationStream(
            randomizedNamespace,
            "test_person_event",
            Append,
            ObjectType(
                linkedMapOf(
                    "person_email" to FieldType(StringType, nullable = false),
                    "event_name" to FieldType(StringType, nullable = false),
                    "an_attribute" to FieldType(StringType, nullable = false)
                ),
                true,
                required = listOf("person_email", "event_name")
            ),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 42,
            destinationObjectName = "person_event",
            namespaceMapper = NamespaceMapper()
        )

    private val personIdentifyStream: DestinationStream =
        DestinationStream(
            randomizedNamespace,
            "test_person_identify",
            Dedupe(emptyList(), emptyList()),
            ObjectType(
                linkedMapOf(
                    "person_email" to FieldType(StringType, nullable = false),
                    "an_attribute" to FieldType(StringType, nullable = false)
                ),
                true,
                required = listOf("person_email")
            ),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 42,
            destinationObjectName = "person_identify",
            namespaceMapper = NamespaceMapper()
        )

    fun personEventRecord(email: String) =
        InputRecord(
            stream = personEventStream,
            data =
                """{"person_email": "$email", "event_name": "integration_test", "an_attribute": "any attribute"}""",
            emittedAtMs = 1234,
        )

    fun personIdentifyRecord(email: String) =
        InputRecord(
            stream = personIdentifyStream,
            data = """{"person_email": "$email", "an_attribute": "any attribute"}""",
            emittedAtMs = 1234,
        )

    @Test
    override fun testBasicWrite() {
        val messages =
            runSync(
                updatedConfig,
                DestinationCatalog(listOf(personEventStream, personIdentifyStream)),
                listOf(
                    personEventRecord("integration-test@airbyte.io"),
                    personIdentifyRecord("integration-test@airbyte.io"),
                    InputStreamCheckpoint(
                        unmappedNamespace = personEventStream.unmappedNamespace,
                        unmappedName = personEventStream.unmappedName,
                        blob = """{}""",
                        sourceRecordCount = 1,
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = personIdentifyStream.unmappedNamespace,
                        unmappedName = personIdentifyStream.unmappedName,
                        blob = """{}""",
                        sourceRecordCount = 1,
                    ),
                ),
            )

        val stateMessages = messages.filter { it.type == AirbyteMessage.Type.STATE }
        assertAll(
            {
                assertEquals(
                    2,
                    stateMessages.size,
                    "Expected to receive one state message per stream (with 2 streams), got ${stateMessages.size} ($stateMessages)"
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
                                data = mapOf("id" to 5678),
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
                        personEventStream,
                        primaryKey = listOf(listOf("id")),
                        cursor = null,
                    )
                }
            },
        )
    }
}
