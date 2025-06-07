package io.airbyte.integrations.destination.shelby

import io.airbyte.cdk.load.discover.DestinationDiscoverer
import io.airbyte.integrations.destination.shelby.http.discover.SalesforceOperationRepository
import io.airbyte.protocol.models.v0.DestinationOperation

class ShelbyDiscoverer(private val operationRepository: SalesforceOperationRepository) : DestinationDiscoverer<ShelbyConfiguration> {
    override fun discover(config: ShelbyConfiguration) {
        val destinationOperations: List<DestinationOperation> = operationRepository.fetchAll()
    }
}
