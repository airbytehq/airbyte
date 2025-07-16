package io.airbyte.cdk.load.discoverer.operation

import io.airbyte.cdk.load.command.DestinationOperation

class CompositeOperationSupplier(private val suppliers: List<OperationSupplier>): OperationSupplier {
    override fun get(): List<DestinationOperation> {
        return suppliers.flatMap { it.get() }
    }
}
