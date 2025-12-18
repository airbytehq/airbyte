/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.test.util

/**
 * Interstitial interface. Most destinations will eventually have a
 * [io.airbyte.cdk.load.component.TableSchemaEvolutionClient] instead.
 */
interface SchemaDumper {
    /**
     * for destinations that already have a TableSchemaEvolutionClient, this is maybe just
     * ```
     * return Jsons.writerWithDefaultPrettyPrinter()
     *   .writeValueAsString(client.discoverSchema(<something>))
     * ```
     * (converting namespace+name to TableName is doable but slightly nontrivial)
     *
     * and then destinations can append other stuff if they want (tablengine, etc.)
     */
    fun discoverSchema(namespace: String?, name: String): String
}
