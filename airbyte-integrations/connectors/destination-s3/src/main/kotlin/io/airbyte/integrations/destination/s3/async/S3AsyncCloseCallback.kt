package io.airbyte.integrations.destination.s3.async

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.function.OnCloseFunction
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.integrations.destination.s3.util.S3StorageOperations
import io.airbyte.integrations.destination.s3.util.WriteConfigGenerator
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Primary
class S3AsyncCloseCallback(
    private val writeConfigGenerator: WriteConfigGenerator,
    private val s3StorageOperations: S3StorageOperations,
): OnCloseFunction {
    override fun accept(hasFailed: Boolean, u: MutableMap<StreamDescriptor, StreamSyncSummary>) {
        if (hasFailed) {
            val writeConfigs = writeConfigGenerator.toWriteConfigs()
            logger.info { "Cleaning up destination started for ${writeConfigs.size} streams" }
            for (writeConfig in writeConfigs) {
                s3StorageOperations.cleanUpBucketObject(writeConfig.fullOutputPath, writeConfig.storedFiles)
                writeConfig.clearStoredFiles()
            }
            logger.info { "Cleaning up destination completed." }
        }
    }
}