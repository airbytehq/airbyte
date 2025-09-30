/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import io.airbyte.cdk.load.command.DestinationDiscoverCatalog
import io.airbyte.cdk.load.discover.DestinationDiscoverer
import io.airbyte.integrations.destination.hubspot.http.HubSpotOperationRepository

class HubSpotDiscoverer(private val operationRepository: HubSpotOperationRepository) :
    DestinationDiscoverer {
    override fun discover(): DestinationDiscoverCatalog {
        return DestinationDiscoverCatalog(operationRepository.fetchAll())
    }
}
