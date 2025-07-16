/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discoverer.`object`

interface DestinationObjectSupplier {
    fun get(): List<DestinationObject>
}
