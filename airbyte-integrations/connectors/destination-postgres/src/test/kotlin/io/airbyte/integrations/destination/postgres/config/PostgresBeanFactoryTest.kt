/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres.config

import io.airbyte.integrations.destination.postgres.spec.CdcDeletionMode
import io.airbyte.integrations.destination.postgres.spec.PostgresConfiguration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertNull
import org.junit.jupiter.api.Test

internal class PostgresBeanFactoryTest {

    private val factory = PostgresBeanFactory()

    private fun configuration(jdbcUrlParams: String? = null): PostgresConfiguration =
        PostgresConfiguration(
            host = "localhost",
            port = 5432,
            database = "db",
            schema = "public",
            username = "user",
            password = "password",
            ssl = false,
            sslMode = null,
            jdbcUrlParams = jdbcUrlParams,
            cdcDeletionMode = CdcDeletionMode.HARD_DELETE,
            legacyRawTablesOnly = false,
            internalTableSchema = null,
            dropCascade = false,
            unconstrainedNumber = false,
            tunnelMethod = null,
        )

    @Test
    fun `data source disables statement timeout by default`() {
        val dataSource =
            factory.postgresDataSource(
                postgresConfiguration = configuration(),
                resolvedHost = "localhost",
                resolvedPort = 5432,
            )

        assertEquals(DISABLE_STATEMENT_TIMEOUT_SQL, dataSource.connectionInitSql)
    }

    @Test
    fun `data source respects a user-provided statement_timeout`() {
        val dataSource =
            factory.postgresDataSource(
                postgresConfiguration =
                    configuration(jdbcUrlParams = "options=-c%20statement_timeout%3D60000"),
                resolvedHost = "localhost",
                resolvedPort = 5432,
            )

        assertNull(dataSource.connectionInitSql)
    }
}
