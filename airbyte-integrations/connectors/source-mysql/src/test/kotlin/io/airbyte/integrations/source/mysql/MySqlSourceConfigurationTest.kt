/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.AIRBYTE_CLOUD_ENV
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.command.SourceConfigurationFactory
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import java.time.Duration
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST, AIRBYTE_CLOUD_ENV], rebuildContext = true)
class MySqlSourceConfigurationTest {
    @Inject
    lateinit var pojoSupplier:
        ConfigurationSpecificationSupplier<MySqlSourceConfigurationSpecification>

    @Inject
    lateinit var factory:
        SourceConfigurationFactory<MySqlSourceConfigurationSpecification, MySqlSourceConfiguration>

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(
        name = "airbyte.connector.config.jdbc_url_params",
        value = "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&"
    )
    fun testParseJdbcParameters() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals(config.realHost, "localhost")
        Assertions.assertEquals(config.realPort, 12345)
        Assertions.assertEquals(config.namespaces, setOf("SYSTEM"))
        Assertions.assertTrue(config.sshTunnel is SshNoTunnelMethod)

        Assertions.assertEquals(config.jdbcProperties["user"], "FOO")
        Assertions.assertEquals(config.jdbcProperties["password"], "BAR")

        // Make sure we don't accidentally drop the following hardcoded settings for mysql.
        Assertions.assertEquals(config.jdbcProperties["useCursorFetch"], "true")
        Assertions.assertEquals(config.jdbcProperties["sessionVariables"], "autocommit=0")

        Assertions.assertEquals(config.jdbcProperties["theAnswerToLiveAndEverything"], "42")
        Assertions.assertEquals(config.jdbcProperties["foo"], "bar")
        // test default value
        Assertions.assertEquals(config.jdbcProperties["sslMode"], "required")
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(name = "airbyte.connector.config.json", value = CONFIG_V1)
    fun testParseConfigFromV1() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals(config.realHost, "localhost")
        Assertions.assertEquals(config.realPort, 12345)
        Assertions.assertEquals(config.namespaces, setOf("SYSTEM"))

        Assertions.assertEquals(config.jdbcProperties["user"], "FOO")
        Assertions.assertEquals(config.jdbcProperties["password"], "BAR")
        Assertions.assertEquals(config.jdbcProperties["sslMode"], "required")
        Assertions.assertTrue(config.incrementalConfiguration is CdcIncrementalConfiguration)

        val cdcCursor = config.incrementalConfiguration as CdcIncrementalConfiguration

        Assertions.assertEquals(cdcCursor.initialLoadTimeout, Duration.ofHours(9))
        Assertions.assertEquals(
            cdcCursor.invalidCdcCursorPositionBehavior,
            InvalidCdcCursorPositionBehavior.RESET_SYNC
        )

        Assertions.assertTrue(config.sshTunnel is SshNoTunnelMethod)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "SYSTEM")
    @Property(name = "airbyte.connector.config.json", value = CONFIG_V2)
    fun testCloudRequirements() {
        val pojo: MySqlSourceConfigurationSpecification = pojoSupplier.get()

        try {
            factory.makeWithoutExceptionHandling(pojo)
            // If we reach here, no exception was thrown - test should fail
            Assertions.fail("Expected ConfigErrorException, but no exception was thrown")
        } catch (e: ConfigErrorException) {
            // Here we verify that the caught exception has the expected message
            Assertions.assertEquals(
                "Connection from Airbyte Cloud requires SSL encryption or an SSH tunnel.",
                e.message
            )
        }
    }
    companion object {

        const val CONFIG_V1: String =
            """
{
  "host": "localhost",
  "port": 12345,
  "database": "SYSTEM",
  "password": "BAR",
  "ssl_mode": {
    "mode": "required"
  },
  "username": "FOO",
  "tunnel_method": {
    "tunnel_method": "NO_TUNNEL"
  },
  "replication_method": {
    "method": "CDC",
    "initial_waiting_seconds": 301,
    "initial_load_timeout_hours": 9,
    "invalid_cdc_cursor_position_behavior": "Re-sync data"
  }
}
"""
        const val CONFIG_V2: String =
            """
{
  "host": "localhost",
  "port": 12345,
  "database": "SYSTEM",
  "password": "BAR",
  "ssl_mode": {
    "mode": "preferred"
  },
  "username": "FOO",
  "tunnel_method": {
    "tunnel_method": "NO_TUNNEL"
  },
  "replication_method": {
    "method": "CDC",
    "initial_waiting_seconds": 301,
    "initial_load_timeout_hours": 9,
    "invalid_cdc_cursor_position_behavior": "Re-sync data"
  }
}
"""
    }
}
