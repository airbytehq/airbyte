/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_v2

import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.load.command.aws.AwsToolkitConstants

class S3V2Destination {
    companion object {
        val additionalMicronautEnvs = listOf(AwsToolkitConstants.MICRONAUT_ENVIRONMENT)

        @JvmStatic
        fun main(args: Array<String>) {
            AirbyteDestinationRunner.run(*args, additionalMicronautEnvs = additionalMicronautEnvs)
        }
    }
}
