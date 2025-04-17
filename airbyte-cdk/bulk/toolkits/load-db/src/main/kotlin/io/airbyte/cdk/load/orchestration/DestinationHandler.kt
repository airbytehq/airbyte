/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.orchestration

interface DestinationHandler {
    fun execute(sql: Sql)

    /**
     * Create the namespaces (typically something like `create schema`).
     *
     * This function should assume that all `namespaces` are valid identifiers, i.e. any special
     * characters have already been escaped, they respect identifier name length, etc.
     */
    suspend fun createNamespaces(namespaces: List<String>)
}
