package io.airbyte.cdk.load.discoverer.operation

import io.airbyte.cdk.load.command.DestinationOperation

interface OperationSupplier {
    fun get(): List<DestinationOperation>
}
