/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.airbyte_context_store

import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.load.command.aws.AwsToolkitConstants

object AirbyteContextStoreDestination {
    val additionalMicronautEnvs = listOf(AwsToolkitConstants.MICRONAUT_ENVIRONMENT)

    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteDestinationRunner.run(*args, additionalMicronautEnvs = additionalMicronautEnvs)
    }
}
