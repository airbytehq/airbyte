package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfiguration

data class ShelbyConfiguration(
    val clientId: String,
    val clientSecret: String,
    val refreshToken: String,
    val isSandbox: Boolean,
) : DestinationConfiguration()
