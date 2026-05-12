/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.connect

import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.integrations.destination.redshift.config.RedshiftConfiguration
import org.junit.jupiter.api.Assertions.assertEquals
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
    fun `createDataSource builds JDBC URL without params`() {
        val connect = RedshiftConnect(config())

        connect.createDataSource().use { ds ->
            assertEquals(
                "jdbc:redshift://my-cluster.redshift.amazonaws.com:5439/mydb",
                ds.jdbcUrl,
            )
        }
    }

    @Test
    fun `createDataSource builds JDBC URL with params`() {
        val connect = RedshiftConnect(config(jdbcUrlParams = "ssl=true&timeout=30"))

        connect.createDataSource().use { ds ->
            assertEquals(
                "jdbc:redshift://my-cluster.redshift.amazonaws.com:5439/mydb?ssl=true&timeout=30",
                ds.jdbcUrl,
            )
        }
    }

    @Test
    fun `createDataSource ignores blank jdbcUrlParams`() {
        val connect = RedshiftConnect(config(jdbcUrlParams = "  "))

        connect.createDataSource().use { ds ->
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
}
