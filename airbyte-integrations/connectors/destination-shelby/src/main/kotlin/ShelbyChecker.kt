package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.check.DestinationChecker

class ShelbyChecker : DestinationChecker<ShelbyConfiguration> {
    override fun check(config: ShelbyConfiguration) {}
}
