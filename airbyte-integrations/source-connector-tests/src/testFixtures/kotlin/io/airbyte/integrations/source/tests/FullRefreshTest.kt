/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */

package io.airbyte.integrations.source.tests

import io.airbyte.protocol.models.v0.SyncMode
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

abstract class FullRefreshTest() : BaseConnectorTest() {

    override fun setupTestData() {
        for (namespace in namespaces) {
            for (table in tables[namespace] ?: emptyList()) {
                testDbInstance.executeUpdate(
                    sqlDialect.buildInsertQuery(table, mapOf("id" to 1, "name" to "foo"))
                )
                testDbInstance.executeUpdate(
                    sqlDialect.buildInsertQuery(table, mapOf("id" to 2, "name" to "bar"))
                )
            }
        }
    }

    override fun cleanupTestData() {
        for (namespace in namespaces) {
            for (table in tables[namespace] ?: emptyList()) {
                testDbInstance.executeUpdate(sqlDialect.buildDeleteQuery(table, null))
            }
        }
    }

    @Test
    fun testEmptyTableSync() {
        cleanupTestData()
        val catalog = getConfiguredCatalog(SyncMode.FULL_REFRESH)
        val outputConsumer = performReadOperation(catalog)

        assertTrue(outputConsumer.records().isEmpty())
    }

    @Test
    fun testSimpleTableSync() {
        val catalog = getConfiguredCatalog(SyncMode.FULL_REFRESH)
        val outputConsumer = performReadOperation(catalog)

        assertEquals(2, outputConsumer.records().size)
    }
}
