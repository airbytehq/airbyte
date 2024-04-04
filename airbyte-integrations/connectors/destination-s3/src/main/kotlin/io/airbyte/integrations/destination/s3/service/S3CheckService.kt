/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.service

import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.integrations.destination.s3.config.properties.S3ConnectorConfiguration
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "check",
)
open class S3CheckService(private val configuration: S3ConnectorConfiguration, private val s3BaseChecks: S3BaseChecks) {
    fun check(): Result<AirbyteMessage?> {
        try {
            configuration.s3BucketName?.let { bucketName ->
                s3BaseChecks.testIAMUserHasListObjectPermission(bucketName)
                configuration.s3BucketPath?.let { bucketPath ->
                    s3BaseChecks.testSingleUpload(bucketName, bucketPath)
                    s3BaseChecks.testMultipartUpload(bucketName, bucketPath)
                }
            }

            return Result.success(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        AirbyteConnectionStatus().withStatus(AirbyteConnectionStatus.Status.SUCCEEDED),
                    ),
            )
        } catch (e: Exception) {
            logger.error(e) { "Exception attempting to access the S3 bucket '${configuration.s3BucketName}'." }
            return Result.success(
                AirbyteMessage()
                    .withType(AirbyteMessage.Type.CONNECTION_STATUS)
                    .withConnectionStatus(
                        AirbyteConnectionStatus()
                            .withStatus(AirbyteConnectionStatus.Status.FAILED)
                            .withMessage("Could not connect to the S3 bucket with the provided configuration. \n ${e.message}"),
                    ),
            )
        }
    }
}
