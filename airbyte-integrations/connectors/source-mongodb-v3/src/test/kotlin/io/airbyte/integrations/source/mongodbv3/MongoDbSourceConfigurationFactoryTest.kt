/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodbv3

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import java.time.Duration
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class MongoDbSourceConfigurationFactoryTest {

    private fun parse(json: String): MongoDbSourceConfigurationSpecification =
        Jsons.readValue(json, MongoDbSourceConfigurationSpecification::class.java)

    private fun make(json: String): MongoDbSourceConfiguration =
        MongoDbSourceConfigurationFactory().makeWithoutExceptionHandling(parse(json))

    @Test
    fun testAtlasConfiguration() {
        val config: MongoDbSourceConfiguration =
            make(
                """
{
  "database_config": {
    "cluster_type": "ATLAS_REPLICA_SET",
    "connection_string": "mongodb+srv://cluster0.abcd1.mongodb.net/",
    "databases": ["db1", "db2"],
    "username": "user",
    "password": "secret",
    "auth_source": "auth_db",
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
""",
            )
        Assertions.assertEquals(MongoDbClusterType.ATLAS_REPLICA_SET, config.clusterType)
        Assertions.assertEquals("mongodb+srv://cluster0.abcd1.mongodb.net/", config.connectionString)
        Assertions.assertEquals(listOf("db1", "db2"), config.databases)
        Assertions.assertEquals("user", config.username)
        Assertions.assertEquals("secret", config.password)
        Assertions.assertTrue(config.hasCredentials)
        Assertions.assertEquals("auth_db", config.authSource)
        Assertions.assertFalse(config.schemaEnforced)
        Assertions.assertEquals(Duration.ofSeconds(600), config.initialWaitingDuration)
        Assertions.assertEquals(5000, config.queueSize)
        Assertions.assertEquals(100, config.discoverSampleSize)
        Assertions.assertEquals(Duration.ofSeconds(60), config.discoverTimeout)
        Assertions.assertEquals(
            InvalidCdcCursorPositionBehavior.RESYNC_DATA,
            config.invalidCdcCursorPositionBehavior,
        )
        Assertions.assertEquals(UpdateCaptureMode.POST_IMAGE, config.updateCaptureMode)
        Assertions.assertEquals(Duration.ofHours(12), config.maxSnapshotReadDuration)
        Assertions.assertEquals("cluster0.abcd1.mongodb.net", config.realHost)
        Assertions.assertEquals(27017, config.realPort)
        Assertions.assertTrue(config.global)
        Assertions.assertEquals(1, config.maxConcurrency)
        Assertions.assertFalse(config.toString().contains("secret"), config.toString())
    }

    @Test
    fun testSelfManagedDefaults() {
        val config: MongoDbSourceConfiguration =
            make(
                """
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "mongodb://host1:27018,host2:27019/?replicaSet=rs0",
    "databases": ["db1"]
  }
}
""",
            )
        Assertions.assertEquals(MongoDbClusterType.SELF_MANAGED_REPLICA_SET, config.clusterType)
        Assertions.assertNull(config.username)
        Assertions.assertNull(config.password)
        Assertions.assertFalse(config.hasCredentials)
        Assertions.assertEquals("admin", config.authSource)
        Assertions.assertTrue(config.schemaEnforced)
        Assertions.assertEquals(Duration.ofSeconds(300), config.initialWaitingDuration)
        Assertions.assertEquals(10000, config.queueSize)
        Assertions.assertEquals(10000, config.discoverSampleSize)
        Assertions.assertEquals(Duration.ofSeconds(600), config.discoverTimeout)
        Assertions.assertEquals(
            InvalidCdcCursorPositionBehavior.FAIL_SYNC,
            config.invalidCdcCursorPositionBehavior,
        )
        Assertions.assertEquals(UpdateCaptureMode.LOOKUP, config.updateCaptureMode)
        Assertions.assertEquals(Duration.ofHours(8), config.maxSnapshotReadDuration)
        Assertions.assertEquals("host1", config.realHost)
        Assertions.assertEquals(27018, config.realPort)
    }

    @Test
    fun testConnectionStringIsSanitizedLikeLegacyConnector() {
        val config: MongoDbSourceConfiguration =
            make(
                """
{
  "database_config": {
    "cluster_type": "ATLAS_REPLICA_SET",
    "connection_string": "  \"mongodb+srv://<username>:<password>@cluster0.abcd1.mongodb.net/\" ",
    "databases": ["db1"],
    "username": "user",
    "password": "secret"
  }
}
""",
            )
        Assertions.assertEquals("mongodb+srv://cluster0.abcd1.mongodb.net/", config.connectionString)
    }

    @Test
    fun testQueueSizeIsClamped() {
        Assertions.assertEquals(1000, make(selfManaged("\"queue_size\": 10")).queueSize)
        Assertions.assertEquals(10000, make(selfManaged("\"queue_size\": 999999")).queueSize)
    }

    @Test
    fun testEmptyDatabasesIsRejected() {
        val exception: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(
                    """
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "mongodb://localhost:27017/",
    "databases": []
  }
}
""",
                )
            }
        Assertions.assertEquals("No databases specified in the configuration.", exception.message)
    }

    /** [MongoDbSourceConfigurationFactory.make] must not hide the user-facing message. */
    @Test
    fun testMakePreservesConfigErrorMessages() {
        val exception: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                MongoDbSourceConfigurationFactory()
                    .make(parse("""{"database_config": {"cluster_type": "SELF_MANAGED_REPLICA_SET", "connection_string": "mongodb://localhost:27017/", "databases": []}}"""))
            }
        Assertions.assertEquals("No databases specified in the configuration.", exception.message)
    }

    @Test
    fun testMalformedConnectionStringIsRejected() {
        val exception: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make(
                    """
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "http://localhost:27017/",
    "databases": ["db1"]
  }
}
""",
                )
            }
        Assertions.assertTrue(
            exception.message!!.startsWith("Invalid connection string:"),
            exception.message,
        )
    }

    @Test
    fun testInvalidEnumValuesAreRejected() {
        Assertions.assertThrows(ConfigErrorException::class.java) {
            make(selfManaged("\"invalid_cdc_cursor_position_behavior\": \"Explode\""))
        }
        Assertions.assertThrows(ConfigErrorException::class.java) {
            make(selfManaged("\"update_capture_mode\": \"Pre Image\""))
        }
    }

    @Test
    fun testSplitHostAndPort() {
        Assertions.assertEquals(
            "localhost" to 27017,
            MongoDbSourceConfigurationFactory.splitHostAndPort("localhost"),
        )
        Assertions.assertEquals(
            "localhost" to 27018,
            MongoDbSourceConfigurationFactory.splitHostAndPort("localhost:27018"),
        )
        Assertions.assertEquals(
            "[::1]" to 27017,
            MongoDbSourceConfigurationFactory.splitHostAndPort("[::1]"),
        )
        Assertions.assertEquals(
            "[::1]" to 27018,
            MongoDbSourceConfigurationFactory.splitHostAndPort("[::1]:27018"),
        )
    }

    private fun selfManaged(extraRootProperty: String): String =
        """
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "mongodb://localhost:27017/",
    "databases": ["db1"]
  },
  $extraRootProperty
}
"""
}
