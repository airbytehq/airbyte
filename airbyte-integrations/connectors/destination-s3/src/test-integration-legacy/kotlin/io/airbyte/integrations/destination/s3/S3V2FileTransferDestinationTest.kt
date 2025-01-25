/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.destination.async.model.AirbyteRecordMessageFile
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3BaseDestinationAcceptanceTest
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.s3.constant.S3Constants
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.*
import io.airbyte.workers.exception.TestHarnessException
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.time.Instant
import kotlin.io.path.createDirectories
import kotlin.io.path.createFile
import kotlin.io.path.writeText
import kotlin.random.Random
import kotlin.test.*
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

private val LOGGER = KotlinLogging.logger {}

class S3V2FileTransferDestinationTest : S3BaseDestinationAcceptanceTest() {
    override val imageName: String = "airbyte/destination-s3:dev"
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
                    Jsons.jsonNode(java.util.Map.of("compression_type", "No Compression")),
                )
            )
    override val baseConfigJson: JsonNode
        get() =
            (super.baseConfigJson as ObjectNode).put(
                S3Constants.S_3_PATH_FORMAT,
                "\${NAMESPACE}/\${STREAM_NAME}/"
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

        fileTransferMountSource!!.resolve(dirPath).createDirectories()
        val absoluteFilePath =
            fileTransferMountSource!!
                .resolve(filePath)
                .createFile()
                .writeText(RandomStringUtils.insecure().nextAlphanumeric(fileSize))
        return Path.of(filePath)
    }

    private fun configureCatalog(streamName: String, generationId: Long): ConfiguredAirbyteCatalog {
        val streamSchema = JsonNodeFactory.instance.objectNode()
        streamSchema.set<JsonNode>("properties", JsonNodeFactory.instance.objectNode())
        return ConfiguredAirbyteCatalog()
            .withStreams(
                java.util.List.of(
                    ConfiguredAirbyteStream()
                        .withSyncMode(SyncMode.INCREMENTAL)
                        .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
                        .withGenerationId(generationId)
                        .withMinimumGenerationId(generationId)
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
    @Disabled
    fun checkRecordSyncFails() {
        val streamName = "str" + RandomStringUtils.insecure().nextAlphanumeric(5)
        val catalog = configureCatalog(streamName, 0)
        val recordBasedMessage =
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(streamName)
                        .withEmittedAt(Instant.now().toEpochMilli())
                        .withData(
                            Jsons.jsonNode(
                                ImmutableMap.builder<Any, Any>()
                                    .put("id", 1)
                                    .put("currency", "USD")
                                    .put("date", "2020-03-31T00:00:00Z")
                                    .put("HKD", 10.1)
                                    .put("NZD", 700.1)
                                    .build(),
                            )
                        )
                )
        try {
            runSyncAndVerifyStateOutput(
                getConfig(),
                listOf(recordBasedMessage, getStreamCompleteMessage(streamName)),
                catalog,
                false
            )
            fail("should have failed!")
        } catch (e: TestHarnessException) {
            assertContains(
                e.outputMessages!![0].trace.error.internalMessage,
                "Failed to construct file message"
            )
        }
    }

    @Test
    fun testFakeFileTransfer() {
        LOGGER.info {
            "${EnvVariableFeatureFlags.DEFAULT_AIRBYTE_STAGING_DIRECTORY} is mounted from $fileTransferMountSource"
        }
        val streamName = "str" + RandomStringUtils.insecure().nextAlphanumeric(5)
        val filePath = createFakeFile()
        val file = fileTransferMountSource!!.resolve(filePath).toFile()
        val fileLength = file.length()
        val fileContent = file.readBytes()
        val catalog = configureCatalog(streamName, 32)
        val recordMessage = createMessageForFile(streamName, filePath)

        runSyncAndVerifyStateOutput(
            getConfig(),
            listOf(recordMessage, getStreamCompleteMessage(streamName)),
            catalog,
            false
        )
        val allObjectsInStore = getAllSyncedObjects(streamName)
        val objectInStore = allObjectsInStore[0]
        val objectMetadata =
            s3Client!!.getObjectMetadata(objectInStore.bucketName, objectInStore.key)
        val generationId =
            objectMetadata
                .getUserMetaDataOf(S3StorageOperations.GENERATION_ID_USER_META_KEY)
                .toLong()
        assertEquals(generationId, 32L)
        assertFalse(file.exists(), "file should have been deleted by the connector")
        assertEquals(fileLength, objectInStore.size)
        assertEquals("$testBucketPath/$streamName/${filePath.toString()}", objectInStore.key)
        assertContentEquals(
            fileContent,
            s3Client!!
                .getObject(objectInStore.bucketName, objectInStore.key)
                .objectContent
                .readBytes()
        )
    }
}
