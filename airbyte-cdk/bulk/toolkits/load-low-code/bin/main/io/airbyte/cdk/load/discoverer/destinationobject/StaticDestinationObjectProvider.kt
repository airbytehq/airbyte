/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.destinationobject

import io.airbyte.cdk.util.Jsons

/**
 * An ObjectProvider generating objects from a statically provided list of object names. The main
 * use case is for standard objects that aren't discoverable dynamically. If used with
 * DynamicDestinationObjectProvider, the namePath should align with what the API returns in case
 * interpolation uses this field.
 */
class StaticDestinationObjectProvider(
    private val objectNames: List<String>,
    private val namePath: String = "name"
) : DestinationObjectProvider {
    override fun get(): List<DestinationObject> {
        return objectNames.map { DestinationObject(it, Jsons.objectNode().put(namePath, it)) }
    }
}
