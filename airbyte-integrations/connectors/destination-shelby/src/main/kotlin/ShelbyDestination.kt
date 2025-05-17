package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.AirbyteDestinationRunner

object ShelbyDestination {
    @JvmStatic
    fun main(args: Array<String>) {
        AirbyteDestinationRunner.run(*args)
    }
}
