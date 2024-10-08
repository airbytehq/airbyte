package io.airbyte.cdk.integrations.destination.s3

import com.amazonaws.services.s3.AmazonS3
import com.amazonaws.services.s3.model.DeleteObjectsRequest
import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.s3.util.S3NameTransformer
import io.airbyte.cdk.integrations.standardtest.destination.AbstractDestinationAcceptanceTest
import io.airbyte.commons.io.IOs
import io.airbyte.commons.json.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import org.apache.commons.lang3.RandomStringUtils
import org.mockito.Mockito
import java.nio.file.Path
import java.util.*

private val LOGGER = KotlinLogging.logger {}

abstract class BaseS3DestinationAcceptanceTest(
    protected val outputFormat: FileUploadFormat,
): AbstractDestinationAcceptanceTest(
    verifyIndividualStateAndCounts = true
) {
    override val imageName: String
        get() = "airbyte/destination-s3:dev"

    protected val secretFilePath: String = "secrets/config.json"
    protected var configJson: JsonNode? = null
    protected var s3DestinationConfig: S3DestinationConfig = Mockito.mock()
    protected var s3Client: AmazonS3? = null
    protected var s3nameTransformer: NamingConventionTransformer = Mockito.mock()
    protected var s3StorageOperations: S3StorageOperations? = null

    protected abstract val formatConfig: JsonNode?
        get

    protected open val baseConfigJson: JsonNode
        get() = Jsons.deserialize(IOs.readFile(Path.of(secretFilePath)))

    fun storageProvider(): StorageProvider {
        return StorageProvider.AWS_S3
    }

    override fun getConfig(): JsonNode = configJson!!

    /**
     * This method does the following:
     * * Construct the S3 destination config.
     * * Construct the S3 client.
     */
    override fun setup(testEnv: AbstractDestinationAcceptanceTest.TestDestinationEnv, TEST_SCHEMAS: HashSet<String>) {
        val baseConfigJson = baseConfigJson
        // Set a random s3 bucket path for each integration test
        val configJson = Jsons.clone(baseConfigJson)
        val testBucketPath =
            String.format(
                "%s_test_%s",
                outputFormat.name.lowercase(),
                RandomStringUtils.insecure().nextAlphanumeric(5),
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
        LOGGER.info {
            "${"Test full path: {}/{}"} ${s3DestinationConfig.bucketName} ${s3DestinationConfig.bucketPath}"
        }

        this.s3Client = s3DestinationConfig.getS3Client()
        this.s3nameTransformer = S3NameTransformer()
        this.s3StorageOperations =
            S3StorageOperations(s3nameTransformer, s3Client!!, s3DestinationConfig)
    }

    /** Remove all the S3 output from the tests. */
    override fun tearDown(testEnv: AbstractDestinationAcceptanceTest.TestDestinationEnv) {
        val keysToDelete: MutableList<DeleteObjectsRequest.KeyVersion> = LinkedList()
        val objects =
            s3Client!!
                .listObjects(s3DestinationConfig.bucketName, s3DestinationConfig.bucketPath)
                .objectSummaries
        for (`object` in objects) {
            keysToDelete.add(DeleteObjectsRequest.KeyVersion(`object`.key))
        }

        if (keysToDelete.size > 0) {
            LOGGER.info {
                "${"Tearing down test bucket path: {}/{}"} ${s3DestinationConfig.bucketName} ${s3DestinationConfig.bucketPath}"
            }
            val result =
                s3Client!!.deleteObjects(
                    DeleteObjectsRequest(s3DestinationConfig.bucketName).withKeys(keysToDelete),
                )
            LOGGER.info { "${"Deleted {} file(s)."} ${result.deletedObjects.size}" }
        }
    }

    override fun inDestinationNormalizationFlags(shouldNormalize: Boolean): Map<String, String> {
        throw NotImplementedError()
    }

    override fun getNormalizationImageName(): String? {
        throw NotImplementedError()
    }

    override fun getNormalizationIntegrationType(): String? {
        throw NotImplementedError()
    }
}
