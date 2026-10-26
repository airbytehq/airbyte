/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.databricks

import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class DatabricksSourceConfigurationTest {

    private val factory = DatabricksSourceConfigurationFactory()

    @Test
    fun testBasicConfigurationWithPersonalAccessToken() {
        // Test basic configuration with personal access token
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                concurrency = 4
                checkpointTargetIntervalSeconds = 300
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify basic properties
        assertEquals("test.databricks.com", config.realHost)
        assertEquals(443, config.realPort)
        assertEquals(setOf("test_database"), config.namespaces)
        assertEquals("test_schema", config.schema)
        assertEquals(4, config.maxConcurrency)
        assertEquals(300L, config.checkpointTargetInterval.seconds)

        // Verify JDBC properties
        assertEquals("3", config.jdbcProperties["AuthMech"])
        assertEquals("token", config.jdbcProperties["UID"])
        assertEquals("test_token_123", config.jdbcProperties["PWD"])
        assertEquals("http", config.jdbcProperties["transportMode"])
        assertEquals("1", config.jdbcProperties["ssl"])
        assertEquals("/sql/1.0/warehouses/test_warehouse", config.jdbcProperties["httpPath"])
        assertEquals("0", config.jdbcProperties["EnableArrow"])
    }

    @Test
    fun testConfigurationWithoutSchema() {
        // Test configuration without schema specification
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = null
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                concurrency = 2
                checkpointTargetIntervalSeconds = 600
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify that schema is null
        assertEquals(null, config.schema)
        assertEquals(setOf("test_database"), config.namespaces)
        assertEquals(2, config.maxConcurrency)
        assertEquals(600L, config.checkpointTargetInterval.seconds)
    }

    @Test
    fun testConfigurationWithJdbcUrlParams() {
        // Test configuration with additional JDBC URL parameters
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                jdbcUrlParams = "application=airbyte&networkTimeout=60000&queryTimeout=300"
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                concurrency = 1
                checkpointTargetIntervalSeconds = 120
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify JDBC URL params are parsed
        assertEquals("airbyte", config.jdbcProperties["application"])
        assertEquals("60000", config.jdbcProperties["networkTimeout"])
        assertEquals("300", config.jdbcProperties["queryTimeout"])

        // Verify other properties are still set
        assertEquals("test_schema", config.schema)
        assertEquals(1, config.maxConcurrency)
    }

    @Test
    fun testConfigurationWithUrlEncodedParams() {
        // Test configuration with URL-encoded parameters
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                jdbcUrlParams = "application=airbyte%20connector&description=test%20connection"
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                concurrency = 1
                checkpointTargetIntervalSeconds = 120
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify URL-encoded params are decoded
        assertEquals("airbyte connector", config.jdbcProperties["application"])
        assertEquals("test connection", config.jdbcProperties["description"])
    }

    @Test
    fun testInvalidConcurrency() {
        // Test that invalid concurrency values throw appropriate errors
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                concurrency = 0 // Invalid value
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                checkpointTargetIntervalSeconds = 300
            }

        assertThrows(ConfigErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }

    @Test
    fun testInvalidCheckpointTargetInterval() {
        // Test that invalid checkpoint target interval values throw appropriate errors
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                concurrency = 4
                checkpointTargetIntervalSeconds = 0 // Invalid value
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
            }

        assertThrows(ConfigErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }

    @Test
    fun testNegativeCheckpointTargetInterval() {
        // Test that negative checkpoint target interval values throw appropriate errors
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                concurrency = 4
                checkpointTargetIntervalSeconds = -1 // Invalid value
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
            }

        assertThrows(ConfigErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }

    @Test
    fun testUnsupportedCredentialsType() {
        // Test that unsupported credentials types throw appropriate errors
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                concurrency = 4
                checkpointTargetIntervalSeconds = 300
                credentials = null // Unsupported credentials type
            }

        assertThrows(ConfigErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }

    @Test
    fun testDefaultValues() {
        // Test that default values are applied correctly
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                concurrency = 4
                checkpointTargetIntervalSeconds = 300
                // Don't set checkPrivileges to test default
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify default values
        assertEquals(true, config.checkPrivileges) // Default should be true
        assertEquals(100L, config.resourceAcquisitionHeartbeat.toMillis()) // Default heartbeat
    }

    @Test
    fun testJdbcUrlFormat() {
        // Test that JDBC URL format is correct
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                concurrency = 4
                checkpointTargetIntervalSeconds = 300
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify JDBC URL format
        assertEquals("jdbc:databricks://%s:%d", config.jdbcUrlFmt)
    }

    @Test
    fun testIncrementalConfiguration() {
        // Test that incremental configuration is set correctly
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                concurrency = 4
                checkpointTargetIntervalSeconds = 300
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify incremental configuration
        assertTrue(config.incremental is UserDefinedCursorIncrementalConfiguration)
        assertEquals(null, config.maxSnapshotReadDuration) // Should be null for user-defined cursor
    }

    @Test
    fun testInvalidJdbcUrlParams() {
        // Test that invalid JDBC URL parameters are handled gracefully
        val spec =
            DatabricksSourceConfigurationSpecification().apply {
                host = "test.databricks.com"
                http_path = "/sql/1.0/warehouses/test_warehouse"
                database = "test_database"
                schema = "test_schema"
                jdbcUrlParams = "invalid_param&another=value&malformed"
                credentials = PersonalAccessTokenCredentialsSpecification(token = "test_token_123")
                concurrency = 4
                checkpointTargetIntervalSeconds = 300
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify that valid params are parsed and invalid ones are ignored
        assertEquals("value", config.jdbcProperties["another"])
        assertTrue(!config.jdbcProperties.containsKey("invalid_param"))
        assertTrue(!config.jdbcProperties.containsKey("malformed"))
    }
}
