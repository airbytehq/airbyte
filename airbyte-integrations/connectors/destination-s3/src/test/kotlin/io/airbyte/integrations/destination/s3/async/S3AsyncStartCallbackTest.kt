package io.airbyte.integrations.destination.s3.async

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.destination.s3.WriteConfig
import io.airbyte.integrations.destination.s3.util.S3StorageOperations
import io.airbyte.integrations.destination.s3.util.WriteConfigGenerator
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.annotation.MockBean
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import jakarta.inject.Inject
import jakarta.inject.Singleton
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST, "destination"], rebuildContext = true)
@Property(name = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION, value = "write")
@Property(name="${ConnectorConfigurationPropertySource.CONNECTOR_CATALOG_PREFIX}.${ConnectorConfigurationPropertySource.CONNECTOR_CATALOG_KEY}",
    value="{\"streams\":[{\"stream\":{\"name\":\"users\",\"namespace\":\"public\"},\"destination_sync_mode\":\"overwrite\"},{\"stream\":{\"name\":\"items\",\"namespace\":\"public\"},\"destination_sync_mode\":\"append\"}]}")
class S3AsyncStartCallbackTest {

    @Inject
    private lateinit var s3AsyncStartCallback: S3AsyncStartCallback
    private val amazonS3Client: AmazonS3 = mockk()
    private val s3StorageOperations: S3StorageOperations = mockk()
    private val writeConfigGenerator: WriteConfigGenerator = mockk()

    @MockBean
    fun amazonS3Client(): AmazonS3 {
        return amazonS3Client
    }

    @Singleton
    @Primary
    fun s3StorageOperations(): S3StorageOperations {
        return s3StorageOperations
    }

    @Singleton
    @Primary
    fun writeConfigGenerator(): WriteConfigGenerator {
        return writeConfigGenerator
    }

    @Test
    internal fun `test that when the callback is invoked, the bucket associated with a stream with destination sync mode overwrite is cleaned up`() {
        val appendFullOutputPath = "/full/output/path/append"
        val appendPathFormat = "append_path_format"
        val appendStoredFiles = listOf("file1","file2","file3")
        val appendStreamName = "items"
        val namespace = "public"
        val overwriteFullOutputPath = "/full/output/path/overwrite"
        val overwriteStreamName = "users"
        val overwriteStoredFiles = listOf("file4","file5","file6")
        val overwritePathFormat = "overwrite_path_format"
        val writeConfigAppend: WriteConfig = mockk()
        val writeConfigOverwrite: WriteConfig = mockk()
        val writeConfigs = listOf(writeConfigOverwrite, writeConfigAppend)

        every { writeConfigAppend.fullOutputPath } returns appendFullOutputPath
        every { writeConfigAppend.namespace } returns namespace
        every { writeConfigAppend.streamName } returns appendStreamName
        every { writeConfigAppend.outputBucketPath } returns appendFullOutputPath
        every { writeConfigAppend.pathFormat } returns appendPathFormat
        every { writeConfigAppend.storedFiles } returns appendStoredFiles
        every { writeConfigAppend.syncMode } returns DestinationSyncMode.APPEND
        every { writeConfigOverwrite.fullOutputPath } returns overwriteFullOutputPath
        every { writeConfigOverwrite.namespace } returns namespace
        every { writeConfigOverwrite.streamName } returns overwriteStreamName
        every { writeConfigOverwrite.outputBucketPath } returns overwriteFullOutputPath
        every { writeConfigOverwrite.pathFormat } returns overwritePathFormat
        every { writeConfigOverwrite.storedFiles } returns overwriteStoredFiles
        every { writeConfigOverwrite.syncMode } returns DestinationSyncMode.OVERWRITE
        every { writeConfigGenerator.toWriteConfigs() } returns writeConfigs
        every { s3StorageOperations.cleanUpBucketObject(namespace, overwriteStreamName, overwriteFullOutputPath, overwritePathFormat) } returns Unit

        s3AsyncStartCallback.voidCall()

        verify(exactly=1) { s3StorageOperations.cleanUpBucketObject(namespace, overwriteStreamName, overwriteFullOutputPath, overwritePathFormat) }
    }
}