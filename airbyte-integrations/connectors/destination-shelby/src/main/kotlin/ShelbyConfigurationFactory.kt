package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import jakarta.inject.Singleton

@Singleton
class ShelbyConfigurationFactory :
    DestinationConfigurationFactory<ShelbySpecification, ShelbyConfiguration> {
    override fun makeWithoutExceptionHandling(pojo: ShelbySpecification): ShelbyConfiguration =
        ShelbyConfiguration()
}
