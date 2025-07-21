/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.operation

import io.airbyte.cdk.load.command.DestinationOperation

/**
 * In some cases, different objects have different rules regarding the operations they support
 * whether it be the insertion methods that are support or the logic through which we identify their
 * matching keys. In this case, the developer should create multiple OperationProviders and pass
 * them through the CompositeOperationProvider.
 */
class CompositeOperationProvider(private val providers: List<OperationProvider>) :
    OperationProvider {
    override fun get(): List<DestinationOperation> {
        return providers.flatMap { it.get() }
    }
}
