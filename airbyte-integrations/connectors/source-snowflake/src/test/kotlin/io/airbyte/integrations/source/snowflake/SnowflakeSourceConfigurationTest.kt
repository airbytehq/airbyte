/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.ConfigErrorException
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.Assertions.assertThrows
import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class SnowflakeSourceConfigurationTest {

    private val factory = SnowflakeSourceConfigurationFactory()

    @Test
    fun testSchemaFilteringWithSpecifiedSchema() {
        // Test that when schema is specified, it's used as the namespace
        val spec =
            SnowflakeSourceConfigurationSpecification().apply {
                host = "test.snowflakecomputing.com"
                role = "TEST_ROLE"
                warehouse = "TEST_WAREHOUSE"
                database = "TEST_DATABASE"
                schema = "PUBLIC" // Specify a schema
                credentials =
                    UsernamePasswordCredentialsSpecification(
                        username = "testuser",
                        password = "testpass"
                    )
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify that namespaces contains the database name (not schema name)
        assertEquals(setOf("TEST_DATABASE"), config.namespaces)

        // Verify that schema is stored separately in the configuration
        assertEquals("PUBLIC", config.schema)

        // Verify that schema is also set in JDBC properties
        assertEquals("PUBLIC", config.jdbcProperties["schema"])

        // Verify database is set correctly in JDBC properties
        assertEquals("TEST_DATABASE", config.jdbcProperties["db"])
    }

    @Test
    fun testSchemaFilteringWithoutSpecifiedSchema() {
        // Test that when schema is not specified, namespaces is empty (allows all schemas)
        val spec =
            SnowflakeSourceConfigurationSpecification().apply {
                host = "test.snowflakecomputing.com"
                role = "TEST_ROLE"
                warehouse = "TEST_WAREHOUSE"
                database = "TEST_DATABASE"
                schema = null // No schema specified
                credentials =
                    UsernamePasswordCredentialsSpecification(
                        username = "testuser",
                        password = "testpass"
                    )
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify that namespaces contains the database name
        assertEquals(setOf("TEST_DATABASE"), config.namespaces)

        // Verify that schema field is null
        assertEquals(null, config.schema)

        // Verify that schema is not in JDBC properties
        assertTrue(!config.jdbcProperties.containsKey("schema"))

        // Verify database is still set correctly
        assertEquals("TEST_DATABASE", config.jdbcProperties["db"])
    }

    @Test
    fun testMultipleSchemasConfiguration() {
        // Test with a specific schema to ensure filtering works
        val spec1 =
            SnowflakeSourceConfigurationSpecification().apply {
                host = "test.snowflakecomputing.com"
                role = "TEST_ROLE"
                warehouse = "TEST_WAREHOUSE"
                database = "TEST_DATABASE"
                schema = "TPCH_SF1"
                credentials =
                    UsernamePasswordCredentialsSpecification(
                        username = "testuser",
                        password = "testpass"
                    )
            }

        val config1 = factory.makeWithoutExceptionHandling(spec1)
        assertEquals(setOf("TEST_DATABASE"), config1.namespaces)
        assertEquals("TPCH_SF1", config1.schema)

        // Test with another schema
        val spec2 =
            SnowflakeSourceConfigurationSpecification().apply {
                host = "test.snowflakecomputing.com"
                role = "TEST_ROLE"
                warehouse = "TEST_WAREHOUSE"
                database = "TEST_DATABASE"
                schema = "INFORMATION_SCHEMA"
                credentials =
                    UsernamePasswordCredentialsSpecification(
                        username = "testuser",
                        password = "testpass"
                    )
            }

        val config2 = factory.makeWithoutExceptionHandling(spec2)
        assertEquals(setOf("TEST_DATABASE"), config2.namespaces)
        assertEquals("INFORMATION_SCHEMA", config2.schema)
    }

    @Test
    fun testJdbcUrlParamsWithSchema() {
        // Test that JDBC URL params work alongside schema specification
        val spec =
            SnowflakeSourceConfigurationSpecification().apply {
                host = "test.snowflakecomputing.com"
                role = "TEST_ROLE"
                warehouse = "TEST_WAREHOUSE"
                database = "TEST_DATABASE"
                schema = "PUBLIC"
                jdbcUrlParams = "application=airbyte&networkTimeout=60000"
                credentials =
                    UsernamePasswordCredentialsSpecification(
                        username = "testuser",
                        password = "testpass"
                    )
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify database is in namespaces, schema is separate
        assertEquals(setOf("TEST_DATABASE"), config.namespaces)
        assertEquals("PUBLIC", config.schema)

        // Verify JDBC params are parsed
        assertEquals("airbyte", config.jdbcProperties["application"])
        assertEquals("60000", config.jdbcProperties["networkTimeout"])

        // Verify schema is still in JDBC properties
        assertEquals("PUBLIC", config.jdbcProperties["schema"])
    }

    @Test
    fun testKeyPairAuthenticationWithSchema() {
        // Test that schema filtering works with key pair authentication
        val spec =
            SnowflakeSourceConfigurationSpecification().apply {
                host = "test.snowflakecomputing.com"
                role = "TEST_ROLE"
                warehouse = "TEST_WAREHOUSE"
                database = "TEST_DATABASE"
                schema = "CUSTOM_SCHEMA"
                credentials =
                    KeyPairCredentialsSpecification(
                        username = "testuser",
                        privateKey = "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
                        privateKeyPassword = "password"
                    )
            }

        val config = factory.makeWithoutExceptionHandling(spec)

        // Verify that namespaces contains the database, schema is separate
        assertEquals(setOf("TEST_DATABASE"), config.namespaces)
        assertEquals("CUSTOM_SCHEMA", config.schema)

        // Verify key pair settings
        assertEquals("testuser", config.jdbcProperties["user"])
        assertEquals("rsa_key.p8", config.jdbcProperties["private_key_file"])
        assertEquals("password", config.jdbcProperties["private_key_file_pwd"])
    }

    @Test
    fun testInvalidConfiguration() {
        // Test that invalid configurations throw appropriate errors
        val spec =
            SnowflakeSourceConfigurationSpecification().apply {
                host = "test.snowflakecomputing.com"
                role = "TEST_ROLE"
                warehouse = "TEST_WAREHOUSE"
                database = "TEST_DATABASE"
                checkpointTargetIntervalSeconds = -1 // Invalid value
                credentials =
                    UsernamePasswordCredentialsSpecification(
                        username = "testuser",
                        password = "testpass"
                    )
            }

        assertThrows(ConfigErrorException::class.java) {
            factory.makeWithoutExceptionHandling(spec)
        }
    }
}
