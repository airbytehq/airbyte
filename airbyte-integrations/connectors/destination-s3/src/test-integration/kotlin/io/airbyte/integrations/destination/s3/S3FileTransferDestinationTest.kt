/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import io.airbyte.cdk.integrations.destination.async.model.AirbyteRecordMessageFile
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3BaseDestinationAcceptanceTest
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.time.Instant
import kotlin.io.path.createDirectories
import kotlin.io.path.createFile
import kotlin.io.path.writeText
import kotlin.random.Random
import kotlin.test.assertEquals
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Test

private val LOGGER = KotlinLogging.logger {}

class S3FileTransferDestinationTest : S3BaseDestinationAcceptanceTest() {
    override val supportsFileTransfer = true
    override val formatConfig: JsonNode
        get() =
            Jsons.jsonNode(
                java.util.Map.of(
                    "format_type",
                    FileUploadFormat.CSV,
                    "flattening",
                    Flattening.ROOT_LEVEL.value,
                    "compression",
                    Jsons.jsonNode(java.util.Map.of("compression_type", "No Compression"))
                )
            )

    private fun getStreamCompleteMessage(streamName: String): AirbyteMessage {
        return AirbyteMessage()
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
    }

    private fun createFakeFile(): Path {
        val depth = Random.nextInt(10)
        val dirPath =
            (0..depth).joinToString("/") {
                "dir" + RandomStringUtils.insecure().nextAlphanumeric(5)
            }
        val fileName = "fakeFile" + RandomStringUtils.insecure().nextAlphanumeric(5)
        val filePath = "$dirPath/$fileName"
        val fileSize = 1_024 * 1_024
        LOGGER.info { "SGX creating director $dirPath inside $fileTransferMountSource" }

        fileTransferMountSource!!.resolve(dirPath).createDirectories()
        LOGGER.info { "SGX creating file $filePath inside $fileTransferMountSource" }
        val absoluteFilePath =
            fileTransferMountSource!!
                .resolve(filePath)
                .createFile()
                .writeText(RandomStringUtils.insecure().nextAlphanumeric(fileSize))
        return Path.of(filePath)
    }

    private fun configureCatalog(streamName: String): ConfiguredAirbyteCatalog {
        val streamSchema = JsonNodeFactory.instance.objectNode()
        streamSchema.set<JsonNode>("properties", JsonNodeFactory.instance.objectNode())
        return ConfiguredAirbyteCatalog()
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
    }

    private fun createMessageForFile(streamName: String, relativeFilePath: Path): AirbyteMessage {
        val absoluteFilePath =
            EnvVariableFeatureFlags.DEFAULT_AIRBYTE_STAGING_DIRECTORY.resolve(relativeFilePath)
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withStream(streamName)
                    .withEmittedAt(Instant.now().toEpochMilli())
                    .withData(ObjectMapper().readTree("{}"))
                    .withAdditionalProperty(
                        "file",
                        AirbyteRecordMessageFile(
                            fileUrl = absoluteFilePath.toString(),
                            bytes = absoluteFilePath.toFile().length(),
                            fileRelativePath = "$relativeFilePath",
                            modified = 123456L,
                            sourceFileUrl = "//sftp-testing-for-file-transfer/$relativeFilePath",
                        )
                    )
            )
    }

    @Test
    fun testFakeFileTransfer() {
        LOGGER.info {
            "${EnvVariableFeatureFlags.DEFAULT_AIRBYTE_STAGING_DIRECTORY} is mounted from $fileTransferMountSource"
        }
        val streamName = "str" + RandomStringUtils.insecure().nextAlphanumeric(5)
        val filePath = createFakeFile()
        val catalog = configureCatalog(streamName)
        val recordMessage = createMessageForFile(streamName, filePath)

        runSyncAndVerifyStateOutput(
            getConfig(),
            listOf(recordMessage, getStreamCompleteMessage(streamName)),
            catalog,
            false
        )
        val allObjectsInStore = getAllSyncedObjects(streamName)
        /*        assertEquals(listOf(filePath.toString()), allObjectsInStore.map { it.key })*/
        val file = fileTransferMountSource!!.resolve(filePath).toFile()
        val objectInStore = allObjectsInStore[0]
        assertEquals(file.length(), objectInStore.size)
        /*assertEquals(
            file.readBytes(),
            s3Client!!
                .getObject(objectInStore.bucketName, objectInStore.key)
                .objectContent
                .readBytes()
        )*/
        LOGGER.info { "SGX getAllSyncedObjects = ${getAllSyncedObjects(streamName)}" }
    }
}
