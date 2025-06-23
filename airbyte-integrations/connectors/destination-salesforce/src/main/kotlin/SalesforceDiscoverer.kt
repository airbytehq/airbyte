/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce

import io.airbyte.cdk.load.command.DestinationDiscoverCatalog
import io.airbyte.cdk.load.discover.DestinationDiscoverer
import io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.SalesforceOperationRepository

class SalesforceDiscoverer(private val operationRepository: SalesforceOperationRepository) :
    DestinationDiscoverer<SalesforceConfiguration> {
    override fun discover(config: SalesforceConfiguration): DestinationDiscoverCatalog {
        return DestinationDiscoverCatalog(operationRepository.fetchAll())
    }
}
