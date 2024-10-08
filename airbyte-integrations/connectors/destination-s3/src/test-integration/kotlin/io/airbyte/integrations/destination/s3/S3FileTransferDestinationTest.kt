package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.integrations.destination.s3.BaseS3DestinationAcceptanceTest
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationAcceptanceTest
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import kotlin.io.path.createFile
import kotlin.io.path.writeText
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Test

private val LOGGER = KotlinLogging.logger {}

class S3FileTransferDestinationTest : BaseS3DestinationAcceptanceTest(FileUploadFormat.CSV) {
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
        LOGGER.info("/file-transfer/ is mounted from $fileTransferMountSource")
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

        val recordMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(streamName)
                        .withEmittedAt(Instant.now().toEpochMilli())
                        .withAdditionalProperty("file", "fakeFile")
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
