/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration.db

import io.airbyte.cdk.load.client.AirbyteClient

interface DatabaseHandler {
    fun execute(sql: Sql)

    /**
     * Create the namespaces (typically something like `create schema`).
     *
     * This function should assume that all `namespaces` are valid identifiers, i.e. any special
     * characters have already been escaped, they respect identifier name length, etc.
     */
    suspend fun createNamespaces(namespaces: Collection<String>)
}

abstract class BaseDatabaseHandler(
    private val airbyteClient: AirbyteClient) : DatabaseHandler {
    override suspend fun createNamespaces(namespaces: Collection<String>) {
        namespaces.forEach { namespace ->
            airbyteClient.createNamespace(namespace)
        }
    }
}
