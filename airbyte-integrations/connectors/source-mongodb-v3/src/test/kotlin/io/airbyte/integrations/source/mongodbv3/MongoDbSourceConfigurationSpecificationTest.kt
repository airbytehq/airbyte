/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

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
    lateinit var supplier: ConfigurationSpecificationSupplier<MongoDbSourceConfigurationSpecification>

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
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
        Assertions.assertEquals(false, databaseConfig.schemaEnforced)

        Assertions.assertEquals(600, pojo.initialWaitingSeconds)
        Assertions.assertEquals(5000, pojo.queueSize)
        Assertions.assertEquals(100, pojo.discoverSampleSize)
        Assertions.assertEquals(60, pojo.discoverTimeoutSeconds)
        Assertions.assertEquals("Re-sync data", pojo.invalidCdcCursorPositionBehavior)
        Assertions.assertEquals("Post Image", pojo.updateCaptureMode)
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
        Assertions.assertEquals(true, databaseConfig.schemaEnforced)
        Assertions.assertEquals(300, pojo.initialWaitingSeconds)
        Assertions.assertEquals(10000, pojo.queueSize)
        Assertions.assertEquals(10000, pojo.discoverSampleSize)
        Assertions.assertEquals(600, pojo.discoverTimeoutSeconds)
        Assertions.assertEquals("Fail sync", pojo.invalidCdcCursorPositionBehavior)
        Assertions.assertEquals("Lookup", pojo.updateCaptureMode)
        Assertions.assertEquals(8, pojo.initialLoadTimeoutHours)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = MISSING_DATABASE_CONFIG_JSON)
    fun testMissingDatabaseConfig() {
        val pojo: MongoDbSourceConfigurationSpecification = supplier.get()
        Assertions.assertNull(pojo.databaseConfigOrNull())
        val exception: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                MongoDbSourceConfigurationFactory().makeWithoutExceptionHandling(pojo)
            }
        Assertions.assertEquals(
            "Database configuration is missing required 'database_config' property.",
            exception.message,
        )
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

        const val MISSING_DATABASE_CONFIG_JSON: String =
            """
{
  "initial_waiting_seconds": 300
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
