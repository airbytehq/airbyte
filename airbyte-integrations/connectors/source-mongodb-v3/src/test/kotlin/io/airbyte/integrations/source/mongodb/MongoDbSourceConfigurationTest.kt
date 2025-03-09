/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb

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

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MongoDbSourceConfigurationTest {
    @Inject
    lateinit var pojoSupplier:
        ConfigurationSpecificationSupplier<MongoDbSourceConfigurationSpecification>

    @Inject
    lateinit var factory:
        SourceConfigurationFactory<
            MongoDbSourceConfigurationSpecification, MongoDbSourceConfiguration>

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_V1)
    fun testParseConfigFromV1() {
        val pojo: MongoDbSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals(
            config.connectionString,
            "mongodb+srv://cluster0.abc45.mongodb.net/"
        )
        Assertions.assertNotNull(config.mongoCredential)
        Assertions.assertTrue(config.schemaEnforced)
        Assertions.assertEquals(config.initialWaitTime, Duration.ofSeconds(301))
        // Default value
        Assertions.assertEquals(config.initialLoadTime, Duration.ofHours(8))
        Assertions.assertEquals(
            config.invalidCdcCursorPositionBehavior,
            MongoDbSourceConfigurationFactory.InvalidCdcCursorPositionBehavior.FAIL_SYNC
        )

        Assertions.assertTrue(config.sshTunnel is SshNoTunnelMethod)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON)
    fun testParseConfigFromSelfManagedInstance() {
        val pojo: MongoDbSourceConfigurationSpecification = pojoSupplier.get()

        val config = factory.makeWithoutExceptionHandling(pojo)

        Assertions.assertEquals(config.connectionString, "mongodb+srv://myDatabaseUser")
        Assertions.assertNull(config.mongoCredential)
        Assertions.assertFalse(config.schemaEnforced)
        Assertions.assertEquals(config.initialWaitTime, Duration.ofSeconds(300))
        Assertions.assertEquals(config.initialLoadTime, Duration.ofHours(3))
        Assertions.assertEquals(
            config.invalidCdcCursorPositionBehavior,
            MongoDbSourceConfigurationFactory.InvalidCdcCursorPositionBehavior.FAIL_SYNC
        )
        Assertions.assertEquals(
            config.captureMode,
            MongoDbSourceConfigurationFactory.CaptureMode.LOOKUP
        )

        Assertions.assertTrue(config.sshTunnel is SshNoTunnelMethod)
    }
}

const val CONFIG_V1: String =
    """
    {
      "queue_size": 10000,
      "database_config": {
        "database": "test_db",
        "password": "123",
        "username": "airbyte_user",
        "auth_source": "admin",
        "cluster_type": "ATLAS_REPLICA_SET",
        "schema_enforced": true,
        "connection_string": "mongodb+srv://cluster0.abc45.mongodb.net/"
      },
      "discover_sample_size": 10000,
      "initial_waiting_seconds": 301,
      "invalid_cdc_cursor_position_behavior": "Fail sync"
    }
  """

const val CONFIG_JSON: String =
    """
{
  "invalid_cdc_cursor_position_behavior": "Fail sync",
  "initial_load_timeout_hours": 3,
  "initial_waiting_seconds": 300,
  "discover_sample_size": 10000,
  "update_capture_mode": "Lookup",
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "mongodb+srv://myDatabaseUser",
    "database": "databasename",
    "schema_enforced": false
  },
  "queue_size": 10000
}
"""
