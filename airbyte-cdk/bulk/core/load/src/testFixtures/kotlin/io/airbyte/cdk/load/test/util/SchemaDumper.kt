/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

/**
 * Interstitial interface. Most destinations will eventually have a
 * [io.airbyte.cdk.load.component.TableSchemaEvolutionClient] instead.
 */
interface SchemaDumper {
    fun discoverSchema(namespace: String?, name: String): String
}
