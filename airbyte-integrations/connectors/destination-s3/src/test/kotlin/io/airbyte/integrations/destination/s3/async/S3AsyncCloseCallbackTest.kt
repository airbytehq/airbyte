package io.airbyte.integrations.destination.s3.async

import com.amazonaws.services.s3.AmazonS3
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_CATALOG_KEY
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource.Companion.CONNECTOR_CATALOG_PREFIX
import io.airbyte.cdk.integrations.destination.s3.WriteConfig
import io.airbyte.integrations.destination.s3.util.S3StorageOperations
import io.airbyte.integrations.destination.s3.util.WriteConfigGenerator
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
@Property(name="${CONNECTOR_CATALOG_PREFIX}.${CONNECTOR_CATALOG_KEY}", value="{\"streams\":[{\"stream\":{\"name\":\"users\",\"namespace\":\"public\"},\"destination_sync_mode\":\"overwrite\"}]}")
class S3AsyncCloseCallbackTest {

    @Inject
    private lateinit var s3AsyncCloseCallback: S3AsyncCloseCallback
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
    internal fun `test that when the async close callback is invoked after a failure, the stored files are cleaned up`() {
        val fullOutputPath = "/full/output/path"
        val storedFiles = listOf("file1","file2","file3")
        val writeConfig: WriteConfig = mockk()
        val writeConfigs = listOf(writeConfig)

        every { writeConfig.fullOutputPath } returns fullOutputPath
        every { writeConfig.storedFiles } returns storedFiles
        every { writeConfig.clearStoredFiles() } returns Unit
        every { writeConfigGenerator.toWriteConfigs() } returns writeConfigs
        every { s3StorageOperations.cleanUpBucketObject(fullOutputPath, storedFiles) } returns Unit

        s3AsyncCloseCallback.accept(true, mutableMapOf())

        verify(exactly=1) { s3StorageOperations.cleanUpBucketObject(fullOutputPath, storedFiles) }
    }

    @Test
    internal fun `test that when the async close callback is invoked after a success, the stored files are not cleaned up`() {
        val fullOutputPath = "/full/output/path"
        val storedFiles = listOf("file1","file2","file3")
        val writeConfig: WriteConfig = mockk()
        val writeConfigs = listOf(writeConfig)

        every { writeConfig.fullOutputPath } returns fullOutputPath
        every { writeConfig.storedFiles } returns storedFiles
        every { writeConfig.clearStoredFiles() } returns Unit
        every { writeConfigGenerator.toWriteConfigs() } returns writeConfigs
        every { s3StorageOperations.cleanUpBucketObject(fullOutputPath, storedFiles) } returns Unit

        s3AsyncCloseCallback.accept(false, mutableMapOf())

        verify(exactly=0) { s3StorageOperations.cleanUpBucketObject(fullOutputPath, storedFiles) }
    }
}