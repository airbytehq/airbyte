/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.discover

import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationDiscoverCatalog

/**
 * A discover operation that is run before the destination is used.
 *
 * * Implementors must provide a [discover] method that returns the catalog.
 * * Implementors may provide a [cleanup] method that is run after the discover is complete.
 * * [discover] should throw an exception if the configuration is invalid.
 * * [cleanup] should not throw exceptions.
 * * Implementors should not perform any side effects in the constructor.
 * * Implementors should not throw exceptions in the constructor.
 * * Implementors should not inject configuration; only use the config passed in [discover].
 */
interface DestinationDiscoverer<C : DestinationConfiguration> {
    fun discover(config: C): DestinationDiscoverCatalog
    fun cleanup(config: C) {}
}
