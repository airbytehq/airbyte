/* Copyright (c) 2025 Airbyte, Inc., all rights reserved. */

package io.airbyte.cdk.test.fixtures.tests

import io.airbyte.cdk.test.fixtures.cleanup.TestAssetResourceNamer
import io.airbyte.cdk.test.fixtures.connector.TestDbExecutor
import io.airbyte.protocol.models.v0.SyncMode
import kotlin.test.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

abstract class FullRefreshTest(
    testDbExecutor: TestDbExecutor,
    testAssetResourceNamer: TestAssetResourceNamer
) : BaseConnectorTest(testDbExecutor, testAssetResourceNamer) {

    override fun setupTestData() {
        for (namespace in namespaces) {
            for (table in tables[namespace] ?: emptyList()) {
                testDbExecutor.executeUpdate(
                    sqlDialect.buildInsertQuery(table, mapOf("id" to 1, "name" to "foo"))
                )
                testDbExecutor.executeUpdate(
                    sqlDialect.buildInsertQuery(table, mapOf("id" to 2, "name" to "bar"))
                )
            }
        }
    }

    override fun cleanupTestData() {
        for (namespace in namespaces) {
            for (table in tables[namespace] ?: emptyList()) {
                testDbExecutor.executeUpdate(sqlDialect.buildDeleteQuery(table, null))
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
