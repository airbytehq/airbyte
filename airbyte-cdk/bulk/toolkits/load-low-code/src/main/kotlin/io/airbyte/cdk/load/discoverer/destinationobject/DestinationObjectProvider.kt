/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.destinationobject

interface DestinationObjectProvider {
    fun get(): List<DestinationObject>
}
