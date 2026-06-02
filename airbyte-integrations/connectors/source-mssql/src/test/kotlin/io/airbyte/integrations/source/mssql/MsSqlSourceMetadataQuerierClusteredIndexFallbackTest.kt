/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import io.airbyte.cdk.command.JdbcSourceConfiguration
import io.airbyte.cdk.discover.JdbcMetadataQuerier
import io.mockk.every
import io.mockk.mockk
import io.mockk.verify
import java.sql.Connection
import java.sql.SQLException
import java.sql.Statement
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test

/**
 * Unit tests for the resilient-fallback behavior of
 * [MsSqlSourceMetadataQuerier.memoizedClusteredIndexKeys].
 *
 * Regression coverage for oncall #12766 / airbyte #78529: against SQL Server-compatible engines
 * such as CData Connect Server, the bulk system-catalog scan over `sys.tables / sys.indexes /
 * sys.index_columns` is rejected with "Insufficient filtering condition in WHERE clause for system
 * table 'indexes'". Previously the connector promoted that error to a [RuntimeException], failing
 * every sync; after the fix it must log a warning and return an empty map so that
 * [MsSqlSourceMetadataQuerier.getOrderedColumnForSync] can fall through to the primary-key /
 * logical-PK paths.
 */
class MsSqlSourceMetadataQuerierClusteredIndexFallbackTest {

    @Test
    @DisplayName(
        "memoizedClusteredIndexKeys returns empty map (not throws) when the system-catalog scan fails"
    )
    fun testClusteredIndexQueryFailureFallsBackGracefully() {
        // The exact wire message reported against CData Connect Server's TDS endpoint.
        val cdataLikeException =
            SQLException(
                "Insufficient filtering condition in WHERE clause for system table 'indexes'"
            )

        val mockStatement =
            mockk<Statement>(relaxed = true) {
                every { executeQuery(any()) } throws cdataLikeException
            }
        val mockConnection =
            mockk<Connection>(relaxed = true) { every { createStatement() } returns mockStatement }
        // Non-empty namespaces drives MsSqlSourceMetadataQuerier.streamNamespaces() to
        // return the configured list directly, so we don't have to mock memoizedTableNames.
        val mockConfig =
            mockk<JdbcSourceConfiguration>(relaxed = true) {
                every { namespaces } returns setOf("dbo")
            }
        val mockBase =
            mockk<JdbcMetadataQuerier>(relaxed = true) {
                every { conn } returns mockConnection
                every { config } returns mockConfig
            }

        val querier = MsSqlSourceMetadataQuerier(mockBase, configuredCatalog = null)

        // The fix swallows the SQLException and returns an empty map instead of
        // re-throwing as a RuntimeException. If the regression returns, this
        // property access will throw and the test will fail.
        val result: Map<*, *> = querier.memoizedClusteredIndexKeys
        assertTrue(
            result.isEmpty(),
            "Expected empty clustered-index map after a vendor-specific filtering error",
        )
        // The executeQuery call should have been attempted exactly once for the
        // (single) configured namespace before the SQLException was swallowed.
        verify(exactly = 1) { mockStatement.executeQuery(any()) }
    }
}
