/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import com.amazonaws.services.s3.model.S3ObjectSummary
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.s3.util.S3NameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.io.IOs
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.util.*
import org.apache.commons.lang3.RandomStringUtils
import org.joda.time.DateTime
import org.joda.time.DateTimeZone
import org.mockito.Mockito.mock

private val LOGGER = KotlinLogging.logger {}
/**
 * When adding a new S3 destination acceptance test, extend this class and do the following:
 * * Implement [.getFormatConfig] that returns a [UploadFormatConfig]
 * * Implement [.retrieveRecords] that returns the Json records for the test
 *
 * Under the hood, a [S3DestinationConfig] is constructed as follows:
 * * Retrieve the secrets from "secrets/config.json"
 * * Get the S3 bucket path from the constructor
 * * Get the format config from [.getFormatConfig]
 */
abstract class S3DestinationAcceptanceTest
protected constructor(protected val outputFormat: FileUploadFormat) : DestinationAcceptanceTest() {
    protected val secretFilePath: String = "secrets/config.json"
    protected var configJson: JsonNode? = null
    protected var s3DestinationConfig: S3DestinationConfig = mock()
    protected var s3Client: AmazonS3? = null
    protected var s3nameTransformer: NamingConventionTransformer = mock()
    protected var s3StorageOperations: S3StorageOperations? = null

    protected open val baseConfigJson: JsonNode
        get() = Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)))

    override val imageName: String
        get() = "airbyte/destination-s3:dev"

    override fun getDefaultSchema(config: JsonNode): String? {
        if (config.has("s3_bucket_path")) {
            return config["s3_bucket_path"].asText()
        }
        return null
    }

    override fun getConfig(): JsonNode = configJson!!

    override fun getFailCheckConfig(): JsonNode {
        val baseJson = baseConfigJson
        val failCheckJson = Jsons.clone(baseJson)
        // invalid credential
        (failCheckJson as ObjectNode).put("access_key_id", "fake-key")
        failCheckJson.put("secret_access_key", "fake-secret")
        return failCheckJson
    }

    /** Helper method to retrieve all synced objects inside the configured bucket path. */
    protected fun getAllSyncedObjects(
        streamName: String,
        namespace: String
    ): List<S3ObjectSummary> {
        val namespaceStr = s3nameTransformer.getNamespace(namespace)
        val streamNameStr = s3nameTransformer.getIdentifier(streamName)
        val outputPrefix =
            s3StorageOperations!!.getBucketObjectPath(
                namespaceStr,
                streamNameStr,
                DateTime.now(DateTimeZone.UTC),
                s3DestinationConfig.pathFormat!!,
            )
        // the child folder contains a non-deterministic epoch timestamp, so use the parent folder
        val parentFolder = outputPrefix.substring(0, outputPrefix.lastIndexOf("/") + 1)
        val objectSummaries =
            s3Client!!
                .listObjects(s3DestinationConfig.bucketName, parentFolder)
                .objectSummaries
                .filter { o: S3ObjectSummary -> o.key.contains("$streamNameStr/") }
                .sortedWith(Comparator.comparingLong { o: S3ObjectSummary -> o.lastModified.time })

        LOGGER.info(
            "All objects: {}",
            objectSummaries.map { o: S3ObjectSummary ->
                String.format("%s/%s", o.bucketName, o.key)
            },
        )
        return objectSummaries
    }

    protected abstract val formatConfig: JsonNode?
        get

    /**
     * This method does the following:
     * * Construct the S3 destination config.
     * * Construct the S3 client.
     */
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        val baseConfigJson = baseConfigJson
        // Set a random s3 bucket path for each integration test
        val configJson = Jsons.clone(baseConfigJson)
        val testBucketPath =
            String.format(
                "%s_test_%s",
                outputFormat.name.lowercase(),
                RandomStringUtils.randomAlphanumeric(5),
            )
        (configJson as ObjectNode)
            .put("s3_bucket_path", testBucketPath)
            .set<JsonNode>("format", formatConfig)
        this.configJson = configJson
        this.s3DestinationConfig =
            S3DestinationConfig.getS3DestinationConfig(
                configJson,
                storageProvider(),
                getConnectorEnv()
            )
        LOGGER.info(
            "Test full path: {}/{}",
            s3DestinationConfig.bucketName,
            s3DestinationConfig.bucketPath,
        )

        this.s3Client = s3DestinationConfig.getS3Client()
        this.s3nameTransformer = S3NameTransformer()
        this.s3StorageOperations =
            S3StorageOperations(s3nameTransformer, s3Client!!, s3DestinationConfig)
    }

    /** Remove all the S3 output from the tests. */
    override fun tearDown(testEnv: TestDestinationEnv) {
        val keysToDelete: MutableList<DeleteObjectsRequest.KeyVersion> = LinkedList()
        val objects =
            s3Client!!
                .listObjects(s3DestinationConfig.bucketName, s3DestinationConfig.bucketPath)
                .objectSummaries
        for (`object` in objects) {
            keysToDelete.add(DeleteObjectsRequest.KeyVersion(`object`.key))
        }

        if (keysToDelete.size > 0) {
            LOGGER.info(
                "Tearing down test bucket path: {}/{}",
                s3DestinationConfig.bucketName,
                s3DestinationConfig.bucketPath,
            )
            val result =
                s3Client!!.deleteObjects(
                    DeleteObjectsRequest(s3DestinationConfig.bucketName).withKeys(keysToDelete),
                )
            LOGGER.info("Deleted {} file(s).", result.deletedObjects.size)
        }
    }

    override fun getTestDataComparator(): TestDataComparator = AdvancedTestDataComparator()

    override fun supportBasicDataTypeTest(): Boolean {
        return true
    }

    override fun supportArrayDataTypeTest(): Boolean {
        return true
    }

    override fun supportObjectDataTypeTest(): Boolean {
        return true
    }

    fun storageProvider(): StorageProvider {
        return StorageProvider.AWS_S3
    }

    companion object {

        @JvmStatic protected val MAPPER: ObjectMapper = MoreMappers.initMapper()
    }
}
