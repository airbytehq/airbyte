/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertFalse
import org.junit.jupiter.api.Test

class RedshiftConnectTest {

    private fun config(
        host: String = "my-cluster.redshift.amazonaws.com",
        port: Int = 5439,
        database: String = "mydb",
        schema: String = "public",
        username: String = "admin",
        password: String = "secret",
        jdbcUrlParams: String? = null,
        tunnelMethod: SshTunnelMethodConfiguration? = null,
    ) =
        RedshiftConfiguration(
            host = host,
            port = port,
            database = database,
            schema = schema,
            username = username,
            password = password,
            jdbcUrlParams = jdbcUrlParams,
            uploadingMethod = null,
            tunnelMethod = tunnelMethod,
            dropCascade = false,
        )

    @Test
    fun `resolveEndpoint returns host and port when tunnel is null`() {
        val connect = RedshiftConnect(config())

        assertEquals("my-cluster.redshift.amazonaws.com:5439", connect.resolveEndpoint())
    }

    @Test
    fun `resolveEndpoint returns host and port with SshNoTunnelMethod`() {
        val connect = RedshiftConnect(config(tunnelMethod = SshNoTunnelMethod))

        assertEquals("my-cluster.redshift.amazonaws.com:5439", connect.resolveEndpoint())
    }

    @Test
    fun `createDataSource builds clean JDBC URL even with jdbcUrlParams`() {
        val connect = RedshiftConnect(config(jdbcUrlParams = "ssl=true&timeout=30"))

        connect.createDataSource().use { ds ->
            // jdbc_url_params are set as data source properties, not appended to the URL
            assertEquals(
                "jdbc:redshift://my-cluster.redshift.amazonaws.com:5439/mydb",
                ds.jdbcUrl,
            )
        }
    }

    @Test
    fun `createDataSource sets credentials and schema`() {
        val connect =
            RedshiftConnect(config(username = "etl_user", password = "p@ss", schema = "raw_data"))

        connect.createDataSource().use { ds ->
            assertEquals("etl_user", ds.username)
            assertEquals("p@ss", ds.password)
            assertEquals("raw_data", ds.schema)
        }
    }

    @Test
    fun `createDataSource sets HikariCP pool configuration`() {
        val connect = RedshiftConnect(config())

        connect.createDataSource().use { ds ->
            assertEquals(120_000L, ds.connectionTimeout) // 2 minutes
            assertEquals(0, ds.minimumIdle)
            assertEquals(-1L, ds.initializationFailTimeout)
        }
    }

    // --- buildConnectionProperties tests ---

    @Test
    fun `buildConnectionProperties returns default SSL properties when no user params`() {
        val connect = RedshiftConnect(config())
        val props = connect.buildConnectionProperties()

        assertEquals("true", props["ssl"])
        assertEquals(RedshiftConnect.SSL_FACTORY, props["sslfactory"])
        assertEquals(2, props.size)
    }

    @Test
    fun `buildConnectionProperties drops sslfactory when user provides sslmode`() {
        val connect = RedshiftConnect(config(jdbcUrlParams = "ssl=true&sslmode=require"))
        val props = connect.buildConnectionProperties()

        assertEquals("true", props["ssl"])
        assertEquals("require", props["sslmode"])
        assertFalse(
            props.containsKey("sslfactory"),
            "sslfactory must be absent when sslmode is set"
        )
        assertEquals(2, props.size)
    }

    @Test
    fun `buildConnectionProperties allows user to override sslfactory`() {
        val connect =
            RedshiftConnect(config(jdbcUrlParams = "sslfactory=com.example.CustomFactory"))
        val props = connect.buildConnectionProperties()

        assertEquals("true", props["ssl"])
        assertEquals("com.example.CustomFactory", props["sslfactory"])
        assertEquals(2, props.size)
    }

    @Test
    fun `buildConnectionProperties preserves non-SSL user params alongside defaults`() {
        val connect = RedshiftConnect(config(jdbcUrlParams = "connectTimeout=60&tcpKeepAlive=true"))
        val props = connect.buildConnectionProperties()

        assertEquals("true", props["ssl"])
        assertEquals(RedshiftConnect.SSL_FACTORY, props["sslfactory"])
        assertEquals("60", props["connectTimeout"])
        assertEquals("true", props["tcpKeepAlive"])
        assertEquals(4, props.size)
    }

    // --- parseJdbcUrlParams tests ---

    @Test
    fun `parseJdbcUrlParams returns empty map for null`() {
        assertEquals(emptyMap<String, String>(), RedshiftConnect.parseJdbcUrlParams(null))
    }

    @Test
    fun `parseJdbcUrlParams returns empty map for blank`() {
        assertEquals(emptyMap<String, String>(), RedshiftConnect.parseJdbcUrlParams("  "))
    }

    @Test
    fun `parseJdbcUrlParams parses key-value pairs`() {
        val result = RedshiftConnect.parseJdbcUrlParams("ssl=true&sslmode=require&timeout=30")

        assertEquals(
            mapOf("ssl" to "true", "sslmode" to "require", "timeout" to "30"),
            result,
        )
    }

    @Test
    fun `parseJdbcUrlParams handles value containing equals sign`() {
        val result = RedshiftConnect.parseJdbcUrlParams("options=-c statement_timeout=5000")

        assertEquals(mapOf("options" to "-c statement_timeout=5000"), result)
    }
}
