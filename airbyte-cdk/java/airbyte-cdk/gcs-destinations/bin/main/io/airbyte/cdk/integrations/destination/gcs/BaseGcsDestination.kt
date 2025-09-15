/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.gcs

import com.amazonaws.services.s3.model.AmazonS3Exception
import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.BaseConnector
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.AirbyteTraceMessageUtility.emitConfigErrorTrace
import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.errors.messages.ErrorMessage.getErrorMessage
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.destination.record_buffer.BufferStorage
import io.airbyte.cdk.integrations.destination.record_buffer.FileBuffer
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks.testMultipartUpload
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks.testSingleUpload
import io.airbyte.cdk.integrations.destination.s3.S3ConsumerFactory
import io.airbyte.cdk.integrations.destination.s3.SerializedBufferFactory.Companion.getCreateFunction
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Consumer
import java.util.function.Function

private val LOGGER = KotlinLogging.logger {}

abstract class BaseGcsDestination : BaseConnector(), Destination {
    private val nameTransformer: NamingConventionTransformer = GcsNameTransformer()

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        try {
            val destinationConfig: GcsDestinationConfig =
                GcsDestinationConfig.Companion.getGcsDestinationConfig(config)
            val s3Client = destinationConfig.getS3Client()

            // Test single upload (for small files) permissions
            testSingleUpload(s3Client, destinationConfig.bucketName, destinationConfig.bucketPath!!)

            // Test multipart upload with stream transfer manager
            testMultipartUpload(
                s3Client,
                destinationConfig.bucketName,
                destinationConfig.bucketPath!!
            )

            return AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED)
        } catch (e: AmazonS3Exception) {
            LOGGER.error(e) { "Exception attempting to access the Gcs bucket" }
            val message = getErrorMessage(e.errorCode, 0, e.message, e)
            emitConfigErrorTrace(e, message)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(message)
        } catch (e: Exception) {
            LOGGER.error(e) {
                "Exception attempting to access the Gcs bucket: {}. Please make sure you account has all of these roles: $EXPECTED_ROLES"
            }
            emitConfigErrorTrace(e, e.message)
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage(
                    "Could not connect to the Gcs bucket with the provided configuration. \n" +
                        e.message
                )
        }
    }

    override fun getConsumer(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        outputRecordCollector: Consumer<AirbyteMessage>
    ): AirbyteMessageConsumer? {
        val gcsConfig: GcsDestinationConfig = GcsDestinationConfig.getGcsDestinationConfig(config)
        return S3ConsumerFactory()
            .create(
                outputRecordCollector,
                GcsStorageOperations(nameTransformer, gcsConfig.getS3Client(), gcsConfig),
                getCreateFunction(
                    gcsConfig,
                    Function<String, BufferStorage> { fileExtension: String ->
                        FileBuffer(fileExtension)
                    }
                ),
                gcsConfig,
                catalog
            )
    }

    companion object {

        const val EXPECTED_ROLES: String =
            ("storage.multipartUploads.abort, storage.multipartUploads.create, " +
                "storage.objects.create, storage.objects.delete, storage.objects.get, storage.objects.list")
    }
}
