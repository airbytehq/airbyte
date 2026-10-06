/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.auth

import io.mockk.Called
import io.mockk.mockk
import io.mockk.verify
import java.net.URLDecoder
import java.nio.charset.StandardCharsets
import java.sql.Driver
import java.util.Properties
import net.snowflake.client.jdbc.SnowflakeConnectString
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

internal class SnowflakeWorkloadIdentityJdbcParserTest {
    @ParameterizedTest
    @ValueSource(strings = ["%C5%BFsl", "s%C5%BFl", "%C5%BF%C5%BFl"])
    fun rejectsUnicodeSslUrlKeysEvenWithExplicitSslTrue(encodedName: String) {
        val url = "$JDBC_URL?$encodedName=false&ssl=true"
        val properties = Properties().apply { setProperty("ssl", "true") }
        // Exercise the actual pinned driver parser without connecting or acquiring credentials.
        // Its equalsIgnoreCase treats long s as s, and ssl=true does not undo the downgrade.
        val parsed = SnowflakeConnectString.parse(url, properties)
        assertTrue(parsed.isValid)
        assertEquals("http", parsed.scheme)
        assertRejectedBeforeConnecting(url, properties)
    }

    @ParameterizedTest
    @ValueSource(strings = ["%C5%BFsl", "s%C5%BFl", "%C5%BF%C5%BFl"])
    fun rejectsUnicodeSslPropertyKeys(encodedName: String) {
        val name = URLDecoder.decode(encodedName, StandardCharsets.UTF_8)
        for (value in listOf("false", "off", false)) {
            val properties =
                Properties().apply {
                    setProperty("ssl", "true")
                    put(name, value)
                }
            val parsed = SnowflakeConnectString.parse(JDBC_URL, properties)
            assertTrue(parsed.isValid)
            assertEquals("http", parsed.scheme)
            assertRejectedBeforeConnecting(JDBC_URL, properties)
            // The connector flattens string-valued Properties defaults before validation.
            if (value is String) {
                assertRejectedBeforeConnecting(JDBC_URL, Properties(properties))
            }
        }
    }

    private fun assertRejectedBeforeConnecting(url: String, properties: Properties) {
        val driver = mockk<Driver>()
        val error =
            assertThrows<IllegalArgumentException> {
                SnowflakeWorkloadIdentityDataSource(
                    jdbcUrl = url,
                    connectionProperties = properties,
                    provider = WorkloadIdentityProvider.OIDC,
                    tokenFilePath = "/not-mounted-yet/token",
                    driver = driver,
                )
            }
        assertEquals(
            "Workload identity JDBC property names must contain only ASCII characters.",
            error.message
        )
        verify { driver wasNot Called }
    }

    companion object {
        private const val JDBC_URL = "jdbc:snowflake://example.snowflakecomputing.com/"
    }
}
