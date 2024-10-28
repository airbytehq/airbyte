/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.s3

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.destination.s3.S3BaseChecks.testCustomEndpointSecured
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfigFactory
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus

class S3DestinationStrictEncrypt : S3Destination {
    constructor() : super()

    @VisibleForTesting
    constructor(
        configFactory: S3DestinationConfigFactory,
        environment: Map<String, String>
    ) : super(configFactory, environment)

    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        val destinationConfig =
            configFactory.getS3DestinationConfig(config, super.storageProvider(), super.environment)

        // Fails early to avoid extraneous validations checks if custom endpoint is not secure
        if (!testCustomEndpointSecured(destinationConfig.endpoint)) {
            return AirbyteConnectionStatus()
                .withStatus(AirbyteConnectionStatus.Status.FAILED)
                .withMessage("Custom endpoint does not use HTTPS")
        }
        return super.check(config)
    }
}
