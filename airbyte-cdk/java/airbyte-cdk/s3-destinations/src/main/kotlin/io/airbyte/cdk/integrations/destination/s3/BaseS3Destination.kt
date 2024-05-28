/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.s3.SerializedBufferFactory.Companion.getCreateFunction
import io.airbyte.cdk.integrations.destination.s3.util.S3NameTransformer
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Consumer
import java.util.function.Function

private val LOGGER = KotlinLogging.logger {}

abstract class BaseS3Destination
protected constructor(
    protected val configFactory: S3DestinationConfigFactory = S3DestinationConfigFactory(),
    protected val environment: Map<String, String> = System.getenv()
) : BaseConnector(), Destination {
    private val nameTransformer: NamingConventionTransformer = S3NameTransformer()

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        try {
            val destinationConfig =
                configFactory.getS3DestinationConfig(config, storageProvider(), environment)
            val s3Client = destinationConfig.getS3Client()

            S3BaseChecks.testIAMUserHasListObjectPermission(s3Client, destinationConfig.bucketName)
            S3BaseChecks.testSingleUpload(
                s3Client,
                destinationConfig.bucketName,
                destinationConfig.bucketPath!!
            )
            S3BaseChecks.testMultipartUpload(
                s3Client,
                destinationConfig.bucketName,
                destinationConfig.bucketPath
            )

            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (e: Exception) {
            LOGGER.error(e) { "Exception attempting to access the S3 bucket: " }
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    "Could not connect to the S3 bucket with the provided configuration. \n" +
                        e.message
                )
        }
    }

    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        val s3Config = configFactory.getS3DestinationConfig(config, storageProvider(), environment)
        return S3ConsumerFactory()
            .create(
                outputRecordCollector,
                S3StorageOperations(nameTransformer, s3Config.getS3Client(), s3Config),
                getCreateFunction(
                    s3Config,
                    Function<String, BufferStorage> { fileExtension: String ->
                        FileBuffer(fileExtension)
                    }
                ),
                s3Config,
                catalog
            )
    }

    abstract fun storageProvider(): StorageProvider

    companion object {}
}
