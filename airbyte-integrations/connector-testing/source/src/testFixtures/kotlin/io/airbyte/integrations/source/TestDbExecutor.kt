/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source

interface TestDbExecutor : AutoCloseable {

    val assetName: String

    fun executeReadQuery(query: String): List<Map<String, Any?>>

    fun executeUpdate(query: String)
}
