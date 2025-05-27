package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

@Factory
class ShelbyBeanFactory {
    @Singleton
    fun check() = ShelbyChecker()

    @Singleton
    fun discover() = ShelbyDiscoverer()

    @Singleton
    fun getConfig(config: DestinationConfiguration) = config as ShelbyConfiguration
}
