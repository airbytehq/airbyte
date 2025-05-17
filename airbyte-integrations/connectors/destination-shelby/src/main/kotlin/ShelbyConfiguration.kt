package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfiguration

data class ShelbyConfiguration(
    val something: String? = null,
) : DestinationConfiguration()
