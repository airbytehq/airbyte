package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.integrations.destination.async.model.AirbyteRecordMessageFile
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3BaseDestinationAcceptanceTest
import io.airbyte.cdk.integrations.destination.s3.S3DestinationAcceptanceTest
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.standardtest.destination.BaseDestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import kotlin.io.path.createFile
import kotlin.io.path.writeText
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Test
import java.util.HashSet

private val LOGGER = KotlinLogging.logger {}

class S3FileTransferDestinationTest : S3BaseDestinationAcceptanceTest() {
    override val supportsFileTransfer = true
    override val formatConfig: JsonNode?
        get() =
            Jsons.jsonNode(
                java.util.Map.of(
                    "format_type",
                    outputFormat,
                    "flattening",
                    Flattening.ROOT_LEVEL.value,
                    "compression",
                    Jsons.jsonNode(java.util.Map.of("compression_type", "No Compression"))
                )
            )

    @Test
    open fun testFakeFileTransfer() {
        fileTransferMountSource!!.resolve("fakeFile").createFile().writeText("file text content!!!")
        LOGGER.info("${EnvVariableFeatureFlags.DEFAULT_AIRBYTE_STAGING_DIRECTORY} is mounted from $fileTransferMountSource")
        val streamSchema = JsonNodeFactory.instance.objectNode()
        streamSchema.set<JsonNode>("properties", JsonNodeFactory.instance.objectNode())
        val streamName = "str" + RandomStringUtils.randomAlphanumeric(5)
        val catalog =
            ConfiguredAirbyteCatalog()
                .withStreams(
                    java.util.List.of(
                        ConfiguredAirbyteStream()
                            .withSyncMode(SyncMode.INCREMENTAL)
                            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                            .withGenerationId(0)
                            .withMinimumGenerationId(0)
                            .withSyncId(0)
                            .withStream(
                                AirbyteStream().withName(streamName).withJsonSchema(streamSchema)
                            ),
                    ),
                )

        val t = AirbyteRecordMessageFile()
        val recordMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(streamName)
                        .withEmittedAt(Instant.now().toEpochMilli())
                        .withData(ObjectMapper().readTree("{}"))
                        .withAdditionalProperty("file", AirbyteRecordMessageFile(
                            fileUrl = "${EnvVariableFeatureFlags.DEFAULT_AIRBYTE_STAGING_DIRECTORY}/fakeFile",
                            bytes=182776,
                            fileRelativePath = "fakeFile",
                            modified= 123456L,
                            sourceFileUrl = "//sftp-testing-for-file-transfer/sftp-folder/simpsons_locations.csv",
                        ))
                )
        val streamCompleteMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.TRACE)
                .withTrace(
                    AirbyteTraceMessage()
                        .withStreamStatus(
                            AirbyteStreamStatusTraceMessage()
                                .withStatus(
                                    AirbyteStreamStatusTraceMessage.AirbyteStreamStatus.COMPLETE
                                )
                                .withStreamDescriptor(StreamDescriptor().withName(streamName))
                        )
                )
        runSyncAndVerifyStateOutput(
            getConfig(),
            listOf(recordMessage, streamCompleteMessage),
            catalog,
            false
        )
    }
}
