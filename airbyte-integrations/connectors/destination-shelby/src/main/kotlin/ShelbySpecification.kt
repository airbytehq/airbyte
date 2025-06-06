package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import jakarta.inject.Singleton

@Singleton
class ShelbySpecification : ConfigurationSpecification()

@Singleton
class ShelbySpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.APPEND,
        )

    override val supportsIncremental = true
}
