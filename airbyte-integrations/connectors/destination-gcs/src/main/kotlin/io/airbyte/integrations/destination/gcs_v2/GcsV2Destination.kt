/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.load.command.aws.AwsToolkitConstants

/**
 * GCS destination entry point. Registers the "aws" Micronaut environment because the GCS client
 * delegates to the S3 client factory via the GCS S3-interop endpoint.
 */
class GcsV2Destination {
    companion object {
        val additionalMicronautEnvs = listOf(AwsToolkitConstants.MICRONAUT_ENVIRONMENT)

        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteDestinationRunner.run(*args, additionalMicronautEnvs = additionalMicronautEnvs)
        }
    }
}
