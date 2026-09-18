/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starrocks.spec

import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Test

class StarrocksConfigurationTest {

    private fun cfg(ssl: Boolean, mode: String = "required", database: String = "db") =
        StarrocksConfiguration(
            host = "h",
            port = 9030,
            httpPort = 8030,
            username = "u",
            password = "p",
            database = database,
            ssl = ssl,
            enableJson = false,
            cdcSoftDelete = false,
            loadAsJson = false,
            sslMode = mode,
        )

    @Test
    fun `jdbcUrl disables SSL when ssl is off, regardless of mode`() {
        assertEquals(
            "jdbc:mysql://h:9030/?sslMode=DISABLED",
            cfg(ssl = false, mode = "required").jdbcUrl
        )
        assertEquals(
            "jdbc:mysql://h:9030/?sslMode=DISABLED",
            cfg(ssl = false, mode = "verify_ca").jdbcUrl
        )
    }

    @Test
    fun `jdbcUrl uses the configured sslMode when ssl is on`() {
        assertEquals(
            "jdbc:mysql://h:9030/?sslMode=REQUIRED",
            cfg(ssl = true, mode = "required").jdbcUrl
        )
        assertEquals(
            "jdbc:mysql://h:9030/?sslMode=VERIFY_CA",
            cfg(ssl = true, mode = "verify_ca").jdbcUrl
        )
        assertEquals(
            "jdbc:mysql://h:9030/?sslMode=VERIFY_IDENTITY",
            cfg(ssl = true, mode = "verify_identity").jdbcUrl,
        )
    }

    @Test
    fun `resolvedDatabase falls back to default when empty`() {
        assertEquals("db", cfg(ssl = false, database = "db").resolvedDatabase)
        assertEquals("default", cfg(ssl = false, database = "").resolvedDatabase)
    }
}
