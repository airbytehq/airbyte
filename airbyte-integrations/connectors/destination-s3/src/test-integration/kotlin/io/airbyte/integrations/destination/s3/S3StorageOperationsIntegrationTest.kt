/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.record_buffer.SerializableBuffer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.destination.s3.StorageProvider
import io.airbyte.cdk.integrations.destination.s3.util.Flattening
import io.airbyte.cdk.integrations.destination.s3.util.S3NameTransformer
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.File
import java.io.InputStream
import java.nio.charset.StandardCharsets
import java.nio.file.Path
import java.util.Map
import java.util.Random
import java.util.stream.Stream
import kotlin.test.assertEquals
import org.apache.commons.lang3.RandomStringUtils
import org.joda.time.DateTime
import org.joda.time.DateTimeZone
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

private val log = KotlinLogging.logger {}

class S3StorageOperationsIntegrationTest {

    private lateinit var s3Client: AmazonS3
    private lateinit var s3StorageOperations: S3StorageOperations
    private lateinit var s3DestinationConfig: S3DestinationConfig
    private val random = Random()
    @BeforeEach
    fun setup() {
        val configJson =
            Jsons.clone(Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json"))))

        val testBucketPath =
            String.format(
                "%s_test_%s",
                FileUploadFormat.CSV.name.lowercase(),
                RandomStringUtils.insecure().nextAlphanumeric(5),
            )
        (configJson as ObjectNode)
            .put("s3_bucket_path", testBucketPath)
            .set<JsonNode>(
                "format",
                Jsons.jsonNode(
                    Map.of(
                        "format_type",
                        FileUploadFormat.CSV,
                        "flattening",
                        Flattening.NO.value,
                        "compression",
                        Jsons.jsonNode(Map.of("compression_type", "No Compression"))
                    )
                )
            )
        s3DestinationConfig =
            S3DestinationConfig.getS3DestinationConfig(
                configJson,
                StorageProvider.AWS_S3,
                emptyMap()
            )

        log.info {
            "Path config for test: ${s3DestinationConfig.bucketName}/${s3DestinationConfig.bucketPath}"
        }

        this.s3Client = s3DestinationConfig.getS3Client()
        this.s3StorageOperations =
            S3StorageOperations(S3NameTransformer(), s3Client, s3DestinationConfig)
    }

    private fun uploadTestRecords(
        namespace: String?,
        objectPrefix: String,
        numOfRecords: Int,
        generationId: Long
    ) {
        log.info { "Uploading $numOfRecords test objects" }
        for (i in 1..numOfRecords) {
            s3StorageOperations.uploadRecordsToBucket(
                createStringBuffer("DummyStringToWrite"),
                namespace,
                objectPrefix,
                generationId
            )
        }
    }

    @Test
    fun testGetLatestGenerationId() {
        val namespace = null
        val streamName = "testStream"
        val outputFormat = "${s3DestinationConfig.bucketPath}/${s3DestinationConfig.pathFormat}"
        val fullObjectPath =
            s3StorageOperations.getBucketObjectPath(
                namespace,
                streamName,
                DateTime.now(DateTimeZone.UTC),
                outputFormat
            )

        // write 12 files with genId 1
        uploadTestRecords(namespace, fullObjectPath, 12, 1)
        // write 10 files with genId 2
        uploadTestRecords(namespace, fullObjectPath, 10, 2)
        // write 5 files with genId 3
        uploadTestRecords(namespace, fullObjectPath, 5, 3)

        // Simulating with smaller pages for test coverage in pagination logic,
        // uploading 1000 objects to simulate maxKeys default of 1000
        // is painfully slower
        // Even S3 copy object isn't any faster for the case of tests if done in single thread.

        val latestGenerationId =
            s3StorageOperations.getStageGenerationInternal(
                namespace,
                streamName,
                s3DestinationConfig.bucketPath!!,
                outputFormat,
                5
            )
        assertEquals(3, latestGenerationId)
    }

    @Test
    fun testListExistingObjects() {
        val namespace = null
        val streamName = "testStream"
        val outputFormat = "${s3DestinationConfig.bucketPath}/${s3DestinationConfig.pathFormat}"
        val fullObjectPath =
            s3StorageOperations.getBucketObjectPath(
                namespace,
                streamName,
                DateTime.now(DateTimeZone.UTC),
                outputFormat
            )

        // write 12 files with genId 1
        uploadTestRecords(namespace, fullObjectPath, 12, 1)
        // write 10 files with genId 2
        uploadTestRecords(namespace, fullObjectPath, 10, 2)
        // write 5 files with genId 3
        uploadTestRecords(namespace, fullObjectPath, 5, 3)

        val existingObjects =
            s3StorageOperations.listExistingObjects(
                namespace,
                streamName,
                s3DestinationConfig.bucketPath!!,
                outputFormat
            )
        assertEquals(27, existingObjects.size)
    }

    @ParameterizedTest
    @MethodSource("listExistingObjectTestDataProvider")
    fun testListExistingObjectsWithGenIdFiltered(
        numberOfGens: Int,
        includeNullGen: Boolean,
        currentGen: Int
    ) {
        val namespace = null
        val streamName = "testStream"
        val outputFormat = "${s3DestinationConfig.bucketPath}/${s3DestinationConfig.pathFormat}"
        val fullObjectPath =
            s3StorageOperations.getBucketObjectPath(
                namespace,
                streamName,
                DateTime.now(DateTimeZone.UTC),
                outputFormat
            )
        var expectedNumberOfObjects = 0
        if (numberOfGens != 0) {
            for (i in 1..numberOfGens) {
                val numberOfObjects =
                    when (val randomNumber = random.nextInt(5)) {
                        0 -> 1
                        else -> randomNumber
                    }
                expectedNumberOfObjects += numberOfObjects
                uploadTestRecords(namespace, fullObjectPath, numberOfObjects, i.toLong())
            }
        }

        // Skip records to insert because the algorithm is
        // tightly dependent on both lastModified and genId to be in the same sorted order
        // This is used to assert non-existent case where currentGen gets decreased from highest Gen
        if (currentGen > numberOfGens) {
            val currentGenObjectSize = random.nextInt(5)
            uploadTestRecords(namespace, fullObjectPath, currentGenObjectSize, currentGen.toLong())
        }

        val existingObjects =
            s3StorageOperations.listExistingObjects(
                namespace,
                streamName,
                s3DestinationConfig.bucketPath!!,
                outputFormat,
                currentGen.toLong()
            )
        assertEquals(expectedNumberOfObjects, existingObjects.size)
    }

    private fun createStringBuffer(strData: String): SerializableBuffer {
        // Intentionally not implementing the methods to see the surface area needed for tests.
        return object : SerializableBuffer {
            private val notImplementedError =
                NotImplementedError("This test should NOT rely on this method call")
            @Deprecated("")
            override fun accept(
                record: AirbyteRecordMessage,
                generationId: Long,
                syncId: Long
            ): Long {
                throw notImplementedError
            }

            override fun accept(
                recordString: String,
                airbyteMetaString: String,
                generationId: Long,
                emittedAt: Long
            ): Long {
                throw notImplementedError
            }

            override fun flush() {
                throw notImplementedError
            }

            override val byteCount: Long
                get() = throw notImplementedError
            override val filename: String
                get() = "UnusedFileNameOnlyForExtension.txt"
            override val file: File
                get() = throw notImplementedError
            override val inputStream: InputStream
                get() = strData.byteInputStream(StandardCharsets.UTF_8)
            override val maxTotalBufferSizeInBytes: Long
                get() = throw notImplementedError
            override val maxPerStreamBufferSizeInBytes: Long
                get() = throw notImplementedError
            override val maxConcurrentStreamsInBuffer: Int
                get() = throw notImplementedError

            override fun close() {
                throw notImplementedError
            }
        }
    }

    @AfterEach
    fun teardown() {
        s3StorageOperations.dropBucketObject(s3DestinationConfig.bucketPath!!)
    }
    companion object {
        @JvmStatic
        private fun listExistingObjectTestDataProvider(): Stream<Arguments> {
            return Stream.of(
                // Ideal case
                Arguments.of(2, false, 3),
                // No existing objects
                Arguments.of(0, false, 3),
                // Jump in genId with gaps
                Arguments.of(4, false, 6),
                // Random non-existent case where genId goes back
                Arguments.of(3, false, 2)
            )
        }
    }
}
