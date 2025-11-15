/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.destinationobject

import io.airbyte.cdk.load.discoverer.operation.extract
import io.airbyte.cdk.load.http.Retriever

/** An ObjectProvider that required performing HTTP requests in order know discover the objects. */
class DynamicDestinationObjectProvider(
    private val retriever: Retriever,
    private val namePath: List<String>
) : DestinationObjectProvider {
    override fun get(): List<DestinationObject> {
        return retriever.getAll().map { DestinationObject(it.extract(namePath).asText(), it) }
    }
}
