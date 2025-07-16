/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.`object`

import io.airbyte.cdk.load.discoverer.operation.extract
import io.airbyte.cdk.load.http.Retriever

/**
 * This class has not been used yet but shows why we structured DestinationObjectSupplier as we did
 */
class DynamicDestinationObjectSupplier(
    private val retriever: Retriever,
    private val namePath: List<String>
) : DestinationObjectSupplier {
    override fun get(): List<DestinationObject> {
        return retriever.getAll().map { DestinationObject(it.extract(namePath).asText(), it) }
    }
}
