/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.`object`

import io.airbyte.cdk.util.Jsons

class StaticDestinationObjectSupplier(
    private val objectNames: List<String>,
    private val key: String = "name"
) : DestinationObjectSupplier {
    override fun get(): List<DestinationObject> {
        return objectNames.map { DestinationObject(it, Jsons.objectNode().put(key, it)) }
    }
}
