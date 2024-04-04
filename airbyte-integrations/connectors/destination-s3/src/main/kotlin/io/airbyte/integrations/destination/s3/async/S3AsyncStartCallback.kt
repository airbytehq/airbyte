package io.airbyte.integrations.destination.s3.async

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.function.OnStartFunction
import io.airbyte.integrations.destination.s3.util.S3StorageOperations
import io.airbyte.integrations.destination.s3.util.WriteConfigGenerator
import io.airbyte.protocol.models.v0.DestinationSyncMode
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
class S3AsyncStartCallback(
    private val writeConfigGenerator: WriteConfigGenerator,
    private val s3StorageOperations: S3StorageOperations,
): OnStartFunction {
    override fun voidCall() {
        val writeConfigs = writeConfigGenerator.toWriteConfigs()
        logger.info { "Preparing bucket in destination started for ${writeConfigs.size} streams" }
        for (writeConfig in writeConfigs) {
            if (writeConfig.syncMode == DestinationSyncMode.OVERWRITE) {
                val namespace = writeConfig.namespace
                val stream = writeConfig.streamName
                val outputBucketPath = writeConfig.outputBucketPath
                val pathFormat = writeConfig.pathFormat
                logger.info { "Clearing storage area in destination started for namespace $namespace stream $stream bucketObject $outputBucketPath pathFormat $pathFormat" }
                s3StorageOperations.cleanUpBucketObject(namespace, stream, outputBucketPath, pathFormat)
                logger.info { "Clearing storage area in destination completed for namespace $namespace stream $stream bucketObject $outputBucketPath" }
            }
        }
        logger.info { "Preparing storage area in destination completed." }
    }
}