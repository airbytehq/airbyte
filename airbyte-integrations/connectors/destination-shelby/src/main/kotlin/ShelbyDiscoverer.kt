package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.discover.DestinationDiscoverer

class ShelbyDiscoverer : DestinationDiscoverer<ShelbyConfiguration<*>> {
    override fun discover(config: ShelbyConfiguration<*>) {
    }
}
