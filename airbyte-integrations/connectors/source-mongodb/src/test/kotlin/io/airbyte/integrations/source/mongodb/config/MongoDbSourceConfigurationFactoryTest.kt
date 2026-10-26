/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mongodb.config

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
        Assertions.assertEquals(
            "mongodb+srv://cluster0.abcd1.mongodb.net/",
            config.connectionString,
        )
        Assertions.assertEquals(listOf("db1", "db2"), config.databases)
        Assertions.assertEquals("user", config.username)
        Assertions.assertEquals("secret", config.password)
        Assertions.assertEquals("user" to "secret", config.credential)
        Assertions.assertEquals("auth_db", config.authSource)
        Assertions.assertFalse(config.schemaEnforced)
        Assertions.assertEquals(100, config.discoverSampleSize)
        Assertions.assertEquals(Duration.ofSeconds(60), config.discoverTimeout)
        Assertions.assertEquals(
            InvalidCdcCursorPositionBehavior.RESYNC_DATA,
            config.invalidCdcCursorPositionBehavior,
        )
        Assertions.assertEquals(Duration.ofHours(12), config.maxSnapshotReadDuration)
        Assertions.assertEquals("cluster0.abcd1.mongodb.net", config.realHost)
        Assertions.assertEquals(27017, config.realPort)
        Assertions.assertTrue(config.global)
        Assertions.assertEquals(1, config.maxConcurrency)
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
        Assertions.assertNull(config.credential)
        Assertions.assertEquals("admin", config.authSource)
        Assertions.assertTrue(config.schemaEnforced)
        Assertions.assertEquals(10000, config.discoverSampleSize)
        Assertions.assertEquals(Duration.ofSeconds(600), config.discoverTimeout)
        Assertions.assertEquals(
            InvalidCdcCursorPositionBehavior.FAIL_SYNC,
            config.invalidCdcCursorPositionBehavior,
        )
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
        Assertions.assertEquals(
            "mongodb+srv://cluster0.abcd1.mongodb.net/",
            config.connectionString,
        )
    }

    /** `make` keeps the message of a configuration error rather than the generic wrap. */
    @Test
    fun testMakePreservesConfigErrorMessages() {
        val exception: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                MongoDbSourceConfigurationFactory()
                    .make(
                        parse(
                            """{"database_config": {"cluster_type": "SELF_MANAGED_REPLICA_SET", "connection_string": "mongodb://localhost:27017/", "databases": ["db1"]}, "update_capture_mode": "x", "invalid_cdc_cursor_position_behavior": "Maybe"}""",
                        ),
                    )
            }
        Assertions.assertEquals(
            "Invalid value 'Maybe' for invalid_cdc_cursor_position_behavior, expected one of [Fail sync, Re-sync data].",
            exception.message,
        )
    }

    /**
     * `schema_enforced` is read from `database_config`, where the spec (and the legacy connector)
     * has it; a root value, which pre-release builds wrote, is only a fallback.
     */
    @Test
    fun testNestedSchemaEnforcedWinsOverTheRootFallback() {
        val config: MongoDbSourceConfiguration =
            make(
                """
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "mongodb://localhost:27017/",
    "databases": ["db1"],
    "schema_enforced": false
  },
  "schema_enforced": true
}
""",
            )
        Assertions.assertFalse(config.schemaEnforced)
        val rootOnly: MongoDbSourceConfiguration =
            make(
                """
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "mongodb://localhost:27017/",
    "databases": ["db1"]
  },
  "schema_enforced": false
}
""",
            )
        Assertions.assertFalse(rootOnly.schemaEnforced)
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
    }

    @Test
    fun testIpv6SeedHostAndDefaultPort() {
        val config =
            MongoDbSourceConfigurationFactory()
                .makeWithoutExceptionHandling(
                    parse(selfManagedWithConnectionString("mongodb://[::1]/")),
                )
        Assertions.assertEquals("::1", config.realHost)
        Assertions.assertEquals(27017, config.realPort)
    }

    private fun selfManagedWithConnectionString(connectionString: String): String =
        """
{
  "database_config": {
    "cluster_type": "SELF_MANAGED_REPLICA_SET",
    "connection_string": "$connectionString",
    "databases": ["db1"]
  }
}
"""

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
