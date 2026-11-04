/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.config

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MongoDbSourceConfigurationSpecificationTest {

    @Inject
    lateinit var supplier:
        ConfigurationSpecificationSupplier<MongoDbSourceConfigurationSpecification>

    /** `database_config` is required by the schema; without it there is no configuration at all. */
    @Test
    fun testNoConfigIsAConfigurationError() {
        Assertions.assertThrows(ConfigErrorException::class.java) {
            MongoDbSourceConfigurationFactory().make(supplier.get())
        }
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = ATLAS_CONFIG_JSON)
    fun testAtlasConfig() {
        val pojo: MongoDbSourceConfigurationSpecification = supplier.get()
        val databaseConfig: DatabaseConfigSpecification = pojo.databaseConfig
        Assertions.assertTrue(
            databaseConfig is AtlasReplicaSetSpecification,
            databaseConfig::class.toString(),
        )
        Assertions.assertEquals(
            "mongodb+srv://cluster0.abcd1.mongodb.net/",
            databaseConfig.connectionString,
        )
        Assertions.assertEquals(listOf("db1", "db2"), databaseConfig.databases)
        Assertions.assertEquals("user", databaseConfig.username)
        Assertions.assertEquals("secret", databaseConfig.password)
        Assertions.assertEquals("admin", databaseConfig.authSource)
        // `schema_enforced` lives inside `database_config`, where the legacy connector had it.
        Assertions.assertNull(pojo.schemaEnforced)
        Assertions.assertEquals(false, databaseConfig.schemaEnforced)
        Assertions.assertFalse(
            MongoDbSourceConfigurationFactory().makeWithoutExceptionHandling(pojo).schemaEnforced,
        )

        // The fixture still carries the dropped legacy `initial_waiting_seconds`/`queue_size`;
        // they are ignored, proving saved v2 configurations keep deserializing.
        Assertions.assertEquals(100, pojo.discoverSampleSize)
        Assertions.assertEquals(60, pojo.discoverTimeoutSeconds)
        Assertions.assertEquals("Re-sync data", pojo.invalidCdcCursorPositionBehavior)
        Assertions.assertEquals(12, pojo.initialLoadTimeoutHours)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = SELF_MANAGED_MINIMAL_CONFIG_JSON)
    fun testSelfManagedMinimalConfigDefaults() {
        val pojo: MongoDbSourceConfigurationSpecification = supplier.get()
        val databaseConfig: DatabaseConfigSpecification = pojo.databaseConfig
        Assertions.assertTrue(
            databaseConfig is SelfManagedReplicaSetSpecification,
            databaseConfig::class.toString(),
        )
        Assertions.assertEquals("mongodb://localhost:27017/", databaseConfig.connectionString)
        Assertions.assertEquals(listOf("db1"), databaseConfig.databases)
        Assertions.assertNull(databaseConfig.username)
        Assertions.assertNull(databaseConfig.password)
        // Defaults advertised by the spec.
        Assertions.assertEquals("admin", databaseConfig.authSource)
        Assertions.assertNull(databaseConfig.schemaEnforced)
        Assertions.assertTrue(
            MongoDbSourceConfigurationFactory().makeWithoutExceptionHandling(pojo).schemaEnforced,
            "schema_enforced defaults to true",
        )
        Assertions.assertEquals(10000, pojo.discoverSampleSize)
        Assertions.assertEquals(600, pojo.discoverTimeoutSeconds)
        Assertions.assertEquals("Fail sync", pojo.invalidCdcCursorPositionBehavior)
        Assertions.assertEquals(8, pojo.initialLoadTimeoutHours)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = UNKNOWN_CLUSTER_TYPE_CONFIG_JSON)
    fun testUnknownClusterType() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    companion object {
        const val ATLAS_CONFIG_JSON: String =
            """
{
  "database_config": {
    "cluster_type": "ATLAS_REPLICA_SET",
    "connection_string": "mongodb+srv://cluster0.abcd1.mongodb.net/",
    "databases": ["db1", "db2"],
    "username": "user",
    "password": "secret",
    "auth_source": "admin",
    "schema_enforced": false
  },
  "initial_waiting_seconds": 600,
  "queue_size": 5000,
  "discover_sample_size": 100,
  "discover_timeout_seconds": 60,
  "invalid_cdc_cursor_position_behavior": "Re-sync data",
  "update_capture_mode": "Post Image",
  "initial_load_timeout_hours": 12
}
"""

        const val SELF_MANAGED_MINIMAL_CONFIG_JSON: String =
            """
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "mongodb://localhost:27017/",
    "databases": ["db1"]
  }
}
"""

        const val UNKNOWN_CLUSTER_TYPE_CONFIG_JSON: String =
            """
{
  "database_config": {
    "cluster_type": "SHARDED_CLUSTER",
    "connection_string": "mongodb://localhost:27017/",
    "databases": ["db1"]
  }
}
"""
    }
}
