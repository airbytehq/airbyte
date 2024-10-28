/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import com.amazonaws.services.s3.model.S3ObjectSummary
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import com.google.common.collect.ImmutableMap
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.s3.FileUploadFormat
import io.airbyte.cdk.integrations.destination.s3.S3StorageOperations
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest
import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator
import io.airbyte.cdk.integrations.standardtest.destination.comparator.TestDataComparator
import io.airbyte.commons.io.IOs
import io.airbyte.commons.jackson.MoreMappers
import io.airbyte.commons.json.Jsons
import io.airbyte.configoss.StandardCheckConnectionOutput
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.github.oshai.kotlinlogging.KotlinLogging
import java.nio.file.Path
import java.util.*
import org.apache.commons.lang3.RandomStringUtils
import org.joda.time.DateTime
import org.joda.time.DateTimeZone
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import org.mockito.Mockito.mock

private val LOGGER = KotlinLogging.logger {}

/**
 * When adding a new GCS destination acceptance test, extend this class and do the following:
 * * Implement [.getFormatConfig] that returns a [S3FormatConfig]
 * * Implement [.retrieveRecords] that returns the Json records for the test
 *
 * Under the hood, a [GcsDestinationConfig] is constructed as follows:
 * * Retrieve the secrets from "secrets/config.json"
 * * Get the GCS bucket path from the constructor
 * * Get the format config from [.getFormatConfig]
 */
abstract class GcsDestinationAcceptanceTest(protected val outputFormat: FileUploadFormat) :
    DestinationAcceptanceTest() {
    protected var configJson: JsonNode? = null
    // Not a big fan of those mocks(). Here to make spotbugs happy
    protected var config: GcsDestinationConfig = mock()
    protected var s3Client: AmazonS3 = mock()
    protected var nameTransformer: NamingConventionTransformer = mock()
    protected var s3StorageOperations: S3StorageOperations? = null

    protected val baseConfigJson: JsonNode
        get() = Jsons.deserialize(IOs.readFile(Path.of(SECRET_FILE_PATH)))

    override fun getProtocolVersion(): ProtocolVersion {
        return ProtocolVersion.V1
    }

    override fun getConfig(): JsonNode {
        return configJson!!
    }

    override fun getDefaultSchema(config: JsonNode): String? {
        if (config.has("gcs_bucket_path")) {
            return config["gcs_bucket_path"].asText()
        }
        return null
    }

    override fun supportBasicDataTypeTest(): Boolean {
        return true
    }

    override fun supportArrayDataTypeTest(): Boolean {
        return true
    }

    override fun supportObjectDataTypeTest(): Boolean {
        return true
    }

    override fun getTestDataComparator(): TestDataComparator {
        return AdvancedTestDataComparator()
    }

    override fun getFailCheckConfig(): JsonNode {
        val baseJson = baseConfigJson
        val failCheckJson = Jsons.clone(baseJson)
        // invalid credential
        (failCheckJson as ObjectNode).put("hmac_key_access_id", "fake-key")
        failCheckJson.put("hmac_key_secret", "fake-secret")
        return failCheckJson
    }

    /** Helper method to retrieve all synced objects inside the configured bucket path. */
    protected fun getAllSyncedObjects(
        streamName: String,
        namespace: String
    ): List<S3ObjectSummary> {
        val namespaceStr = nameTransformer.getNamespace(namespace)
        val streamNameStr = nameTransformer.getIdentifier(streamName)
        val outputPrefix =
            s3StorageOperations!!.getBucketObjectPath(
                namespaceStr,
                streamNameStr,
                DateTime.now(DateTimeZone.UTC),
                config.pathFormat!!
            )
        // the child folder contains a non-deterministic epoch timestamp, so use the parent folder
        val parentFolder = outputPrefix.substring(0, outputPrefix.lastIndexOf("/") + 1)
        val objectSummaries =
            s3Client
                .listObjects(config.bucketName, parentFolder)
                .objectSummaries
                .filter { o: S3ObjectSummary -> o.key.contains("$streamNameStr/") }
                .sortedWith(Comparator.comparingLong { o: S3ObjectSummary -> o.lastModified.time })
        LOGGER.info(
            "All objects: {}",
            objectSummaries.map { o: S3ObjectSummary ->
                String.format("%s/%s", o.bucketName, o.key)
            }
        )
        return objectSummaries
    }

    protected abstract val formatConfig: JsonNode?
        get

    /**
     * This method does the following:
     * * Construct the GCS destination config.
     * * Construct the GCS client.
     */
    override fun setup(testEnv: TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        val baseConfigJson = baseConfigJson
        // Set a random GCS bucket path for each integration test
        val configJson = Jsons.clone(baseConfigJson)
        val testBucketPath =
            String.format(
                "%s_test_%s",
                outputFormat.name.lowercase(),
                RandomStringUtils.randomAlphanumeric(5)
            )
        (configJson as ObjectNode)
            .put("gcs_bucket_path", testBucketPath)
            .set<JsonNode>("format", formatConfig)
        this.configJson = configJson
        this.config = GcsDestinationConfig.getGcsDestinationConfig(configJson)
        LOGGER.info("Test full path: {}/{}", config.bucketName, config.bucketPath)

        this.s3Client = config.getS3Client()
        this.nameTransformer = GcsNameTransformer()
        this.s3StorageOperations = S3StorageOperations(nameTransformer, s3Client!!, config)
    }

    /** Remove all the S3 output from the tests. */
    override fun tearDown(testEnv: TestDestinationEnv) {
        val keysToDelete: MutableList<DeleteObjectsRequest.KeyVersion> = LinkedList()
        val objects = s3Client.listObjects(config!!.bucketName, config!!.bucketPath).objectSummaries
        for (`object` in objects) {
            keysToDelete.add(DeleteObjectsRequest.KeyVersion(`object`.key))
        }

        if (keysToDelete.size > 0) {
            LOGGER.info(
                "Tearing down test bucket path: {}/{}",
                config!!.bucketName,
                config!!.bucketPath
            )
            // Google Cloud Storage doesn't accept request to delete multiple objects
            for (keyToDelete in keysToDelete) {
                s3Client!!.deleteObject(config!!.bucketName, keyToDelete.key)
            }
            LOGGER.info("Deleted {} file(s).", keysToDelete.size)
        }
    }

    /**
     * Verify that when given user with no Multipart Upload Roles, that check connection returns a
     * failed response. Assume that the #getInsufficientRolesFailCheckConfig() returns the service
     * account has storage.objects.create permission but not storage.multipartUploads.create.
     */
    @Test
    @Throws(Exception::class)
    fun testCheckConnectionInsufficientRoles() {
        val baseConfigJson =
            Jsons.deserialize(IOs.readFile(Path.of(SECRET_FILE_PATH_INSUFFICIENT_ROLES)))

        // Set a random GCS bucket path for each integration test
        val configJson = Jsons.clone(baseConfigJson)
        val testBucketPath =
            String.format(
                "%s_test_%s",
                outputFormat.name.lowercase(),
                RandomStringUtils.randomAlphanumeric(5)
            )
        (configJson as ObjectNode)
            .put("gcs_bucket_path", testBucketPath)
            .set<JsonNode>("format", formatConfig)

        Assertions.assertEquals(
            StandardCheckConnectionOutput.Status.FAILED,
            runCheck(configJson).status
        )
    }

    @Test
    fun testCheckIncorrectHmacKeyAccessIdCredential() {
        val baseJson = baseConfigJson
        val credential =
            Jsons.jsonNode(
                ImmutableMap.builder<Any, Any>()
                    .put("credential_type", "HMAC_KEY")
                    .put("hmac_key_access_id", "fake-key")
                    .put("hmac_key_secret", baseJson["credential"]["hmac_key_secret"].asText())
                    .build()
            )

        (baseJson as ObjectNode).put("credential", credential)
        baseJson.set<JsonNode>("format", formatConfig)

        val destination: BaseGcsDestination = object : BaseGcsDestination() {}
        val status = destination.check(baseJson)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
        Assertions.assertTrue(status.message.contains("State code: SignatureDoesNotMatch;"))
    }

    @Test
    fun testCheckIncorrectHmacKeySecretCredential() {
        val baseJson = baseConfigJson
        val credential =
            Jsons.jsonNode(
                ImmutableMap.builder<Any, Any>()
                    .put("credential_type", "HMAC_KEY")
                    .put(
                        "hmac_key_access_id",
                        baseJson["credential"]["hmac_key_access_id"].asText()
                    )
                    .put("hmac_key_secret", "fake-secret")
                    .build()
            )

        (baseJson as ObjectNode).put("credential", credential)
        baseJson.set<JsonNode>("format", formatConfig)

        val destination: BaseGcsDestination = object : BaseGcsDestination() {}
        val status = destination.check(baseJson)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
        Assertions.assertTrue(status.message.contains("State code: SignatureDoesNotMatch;"))
    }

    @Test
    fun testCheckIncorrectBucketCredential() {
        val baseJson = baseConfigJson
        (baseJson as ObjectNode).put("gcs_bucket_name", "fake_bucket")
        baseJson.set<JsonNode>("format", formatConfig)

        val destination: BaseGcsDestination = object : BaseGcsDestination() {}
        val status = destination.check(baseJson)
        Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status!!.status)
        Assertions.assertTrue(status.message.contains("State code: NoSuchKey;"))
    }

    companion object {
        @JvmStatic protected val MAPPER: ObjectMapper = MoreMappers.initMapper()

        protected const val SECRET_FILE_PATH: String = "secrets/config.json"
        protected const val SECRET_FILE_PATH_INSUFFICIENT_ROLES: String =
            "secrets/insufficient_roles_config.json"
    }
}
