/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.NamespaceMapper
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.data.BooleanType
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.NumberType
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
import io.airbyte.integrations.destination.hubspot.HubSpotSpecification
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

class HubSpotDataDumper : DestinationDataDumper {
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

object HubSpotDataCleaner : DestinationCleaner {
    override fun cleanup() {}
}

class HubSpotWriterTest() :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(Path.of("secrets/config.json")),
        configSpecClass = HubSpotSpecification::class.java,
        dataDumper = HubSpotDataDumper(),
        destinationCleaner = HubSpotDataCleaner,
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

    private val contactStream: DestinationStream =
        DestinationStream(
            randomizedNamespace,
            "test_stream_contact",
            Update,
            ObjectType(
                linkedMapOf(
                    "email" to FieldType(StringType, nullable = true),
                    "hs_enriched_email_bounce_detected" to FieldType(BooleanType, nullable = true)
                )
            ),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 42,
            destinationObjectName = "CONTACT",
            namespaceMapper = NamespaceMapper(),
            matchingKey = listOf("email"),
        )

    private val companyStream: DestinationStream =
        DestinationStream(
            randomizedNamespace,
            "test_stream_companies",
            Update,
            ObjectType(
                linkedMapOf(
                    "retl_identifier" to FieldType(StringType, nullable = true),
                    "about_us" to FieldType(StringType, nullable = true)
                )
            ),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 42,
            destinationObjectName = "COMPANY",
            namespaceMapper = NamespaceMapper(),
            matchingKey = listOf("retl_identifier"),
        )

    private val carsStream: DestinationStream =
        DestinationStream(
            randomizedNamespace,
            "test_stream_cars",
            Update,
            ObjectType(
                linkedMapOf(
                    "car_id" to FieldType(StringType, nullable = true),
                    "hs_object_source_detail_1" to FieldType(NumberType, nullable = true)
                )
            ),
            generationId = 0,
            minimumGenerationId = 0,
            syncId = 42,
            destinationObjectName = "cars",
            namespaceMapper = NamespaceMapper(),
            matchingKey = listOf("car_id"),
        )

    fun contactRecord(email: String) =
        InputRecord(
            stream = contactStream,
            data = """{"email": "$email", "hs_clicked_linkedin_ad": "false"}""",
            emittedAtMs = 1234,
        )

    fun companyRecord(retlIdentifier: String) =
        InputRecord(
            stream = companyStream,
            data =
                """{"retl_identifier": "$retlIdentifier", "about_us": "This about_us has been generated by integration tests"}""",
            emittedAtMs = 1234,
        )

    fun carsRecord(carId: Int) =
        InputRecord(
            stream = carsStream,
            data = """{"car_id": $carId, "hubspot_owner_id": "52550153"}""",
            emittedAtMs = 1234,
        )

    @Test
    override fun testBasicWrite() {
        val messages =
            runSync(
                updatedConfig,
                DestinationCatalog(listOf(contactStream, companyStream, carsStream)),
                listOf(
                    contactRecord("mcl.retl.test@airbyte-x.com"),
                    companyRecord("retl_id"),
                    carsRecord(1000),
                    InputStreamCheckpoint(
                        unmappedNamespace = contactStream.mappedDescriptor.namespace,
                        unmappedName = contactStream.mappedDescriptor.name,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = companyStream.mappedDescriptor.namespace,
                        unmappedName = companyStream.mappedDescriptor.name,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                    ),
                    InputStreamCheckpoint(
                        unmappedNamespace = carsStream.mappedDescriptor.namespace,
                        unmappedName = carsStream.mappedDescriptor.name,
                        blob = """{"foo": "bar"}""",
                        sourceRecordCount = 1,
                    )
                ),
            )

        val stateMessages = messages.filter { it.type == AirbyteMessage.Type.STATE }
        assertAll(
            {
                assertEquals(
                    3,
                    stateMessages.size,
                    "Expected to receive exactly three state messages (one for each stream), got ${stateMessages.size} ($stateMessages)"
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
                        contactStream,
                        primaryKey = listOf(listOf("email")),
                        cursor = null,
                    )
                }
            },
        )
    }
}
