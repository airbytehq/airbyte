package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.AirbyteDestinationRunner
import io.airbyte.cdk.load.command.aws.AwsToolkitConstants

object ShelbyDestination {
    val additionalMicronautEnvs = listOf(AwsToolkitConstants.MICRONAUT_ENVIRONMENT)

    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteDestinationRunner.run(*args, additionalMicronautEnvs = additionalMicronautEnvs)
    }
}
