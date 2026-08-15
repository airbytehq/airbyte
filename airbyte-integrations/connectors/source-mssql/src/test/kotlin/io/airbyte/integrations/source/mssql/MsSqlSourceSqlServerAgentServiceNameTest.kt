/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql

import java.util.stream.Stream
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.MethodSource

class MsSqlSourceSqlServerAgentServiceNameTest {

    @Test
    fun `agent lookup queries sys dm_server_services with two LIKE patterns`() {
        assertEquals(
            listOf("%SQL Server%Agent%", "%SQL Server 代理%"),
            likePatternsInAgentQuery(),
        )
    }

    @ParameterizedTest
    @MethodSource("serviceNameCases")
    fun `LIKE patterns match localized SQL Server Agent service names`(
        serviceName: String,
        expectedMatch: Boolean,
    ) {
        // Patterns are read back out of the query the connector actually runs, so this fails if the
        // query stops using them.
        val patterns = likePatternsInAgentQuery()
        val matches =
            patterns.any { pattern ->
                serviceName.matches(
                    pattern.split("%").joinToString(".*") { Regex.escape(it) }.toRegex()
                )
            }
        assertEquals(expectedMatch, matches) {
            "patterns=$patterns serviceName='$serviceName'"
        }
    }

    companion object {
        /** Extracts every `LIKE '...'` literal from the production agent-service query. */
        private fun likePatternsInAgentQuery(): List<String> =
            Regex("LIKE '([^']*)'")
                .findAll(MsSqlSourceMetadataQuerier.SQL_SERVER_AGENT_SERVICE_QUERY)
                .map { it.groupValues[1] }
                .toList()

        @JvmStatic
        fun serviceNameCases(): Stream<Arguments> =
            Stream.of(
                Arguments.of("SQL Server Agent", true),
                Arguments.of("SQL Server-Agent", true),
                Arguments.of("SQL Server  Agent", true),
                Arguments.of("SQL Server Agent (MSSQLSERVER)", true),
                Arguments.of("SQL Server-Agent (MSSQLSERVER)", true),
                Arguments.of("SQL Server Agent (EXPRESS)", true),
                Arguments.of("SQL Server 代理", true),
                Arguments.of("SQL Server 代理 (MSSQLSERVER)", true),
                Arguments.of("SQL Server Browser", false),
                Arguments.of("SQL Agent", false),
                Arguments.of("Agent", false),
                Arguments.of("", false),
                Arguments.of("Unrelated Service", false),
            )
    }
}
