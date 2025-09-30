/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import io.airbyte.cdk.load.command.DestinationOperation
import io.airbyte.cdk.load.discoverer.destinationobject.DestinationObjectProvider

class DynamicOperationProvider(
    private val objectsSupplier: DestinationObjectProvider,
    private val operationAssembler: DestinationOperationAssembler
) : OperationProvider {

    override fun get(): List<DestinationOperation> {
        return objectsSupplier.get().flatMap { operationAssembler.assemble(it) }
    }
}
