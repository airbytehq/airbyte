package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

@Singleton
class ShelbyConfigurationFactory :
    DestinationConfigurationFactory<ShelbySpecification, ShelbyConfiguration> {
    override fun makeWithoutExceptionHandling(spec: ShelbySpecification): ShelbyConfiguration =
        ShelbyConfiguration(spec.clientId, spec.clientSecret, spec.refreshToken, spec.isSandbox)
}
