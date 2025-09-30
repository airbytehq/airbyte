/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import io.airbyte.cdk.load.command.DestinationDiscoverCatalog
import io.airbyte.cdk.load.discover.DestinationDiscoverer
import io.airbyte.cdk.load.discoverer.operation.OperationProvider

class CustomerIoDiscoverer(private val operationProvider: OperationProvider) :
    DestinationDiscoverer {
    override fun discover(): DestinationDiscoverCatalog {
        return DestinationDiscoverCatalog(operationProvider.get())
    }
}
