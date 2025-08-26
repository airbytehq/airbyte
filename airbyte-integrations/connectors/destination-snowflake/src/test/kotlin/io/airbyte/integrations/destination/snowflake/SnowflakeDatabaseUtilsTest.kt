/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.snowflake

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import com.zaxxer.hikari.HikariDataSource
import io.airbyte.cdk.db.jdbc.JdbcUtils
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test

class SnowflakeDatabaseUtilsTest {

    private val mapper = ObjectMapper()

    @Test
    fun testCreateDataSourceIncludesWarehouse() {
        // Given: A standard Snowflake configuration
        val config = createTestConfig()

        // When: Creating a regular data source
        val dataSource = SnowflakeDatabaseUtils.createDataSource(config, "test-env")

        // Then: The data source should have warehouse property set
        assertNotNull(dataSource)
        assertTrue(dataSource is HikariDataSource)
        val hikariDataSource = dataSource as HikariDataSource
        val properties = hikariDataSource.dataSourceProperties

        assertEquals("TEST_WAREHOUSE", properties.getProperty("warehouse"))
        assertEquals("test-env", properties.getProperty("application"))
    }

    @Test
    fun testCreateMetadataDataSourceExcludesWarehouse() {
        // Given: A standard Snowflake configuration
        val config = createTestConfig()

        // When: Creating a metadata data source
        val dataSource = SnowflakeDatabaseUtils.createMetadataDataSource(config, "test-env")

        // Then: The data source should NOT have warehouse property set
        assertNotNull(dataSource)
        assertTrue(dataSource is HikariDataSource)
        val hikariDataSource = dataSource as HikariDataSource
        val properties = hikariDataSource.dataSourceProperties

        // Verify warehouse is NOT set
        assertNull(
            properties.getProperty("warehouse"),
            "Warehouse should not be set for metadata connections to avoid compute costs"
        )

        // Verify other properties are still set correctly
        assertEquals("TEST_DATABASE", properties.getProperty(JdbcUtils.DATABASE_KEY))
        assertEquals("TEST_ROLE", properties.getProperty("role"))
        // Schema name gets processed by name transformer
        assertNotNull(properties.getProperty(JdbcUtils.SCHEMA_KEY))
        assertEquals("test-env-metadata", properties.getProperty("application"))

        // Verify connection pool is optimized for metadata queries
        assertEquals(
            2,
            hikariDataSource.maximumPoolSize,
            "Metadata connection should have smaller pool size"
        )
        assertEquals(
            1,
            hikariDataSource.minimumIdle,
            "Metadata connection should have minimal idle connections"
        )
    }

    @Test
    fun testMetadataDataSourceWithPasswordAuth() {
        // Given: A Snowflake configuration with password authentication
        val config = createTestConfig()

        // When: Creating a metadata data source
        val dataSource = SnowflakeDatabaseUtils.createMetadataDataSource(config, "test-env")

        // Then: Password auth should work and warehouse should not be set
        assertTrue(dataSource is HikariDataSource)
        val hikariDataSource = dataSource as HikariDataSource
        val properties = hikariDataSource.dataSourceProperties

        assertNull(
            properties.getProperty("warehouse"),
            "Warehouse should not be set for metadata connection"
        )
        assertEquals("test_user", hikariDataSource.username)
        assertEquals("test_password", hikariDataSource.password)
    }

    @Test
    fun testMetadataDataSourceWithKeyPair() {
        // Given: A Snowflake configuration with key pair authentication
        val config = createTestConfigWithKeyPair()

        // When: Creating a metadata data source with key pair
        val dataSource = SnowflakeDatabaseUtils.createMetadataDataSource(config, "test-env")

        // Then: Key pair properties should be set, but warehouse should not
        assertTrue(dataSource is HikariDataSource)
        val hikariDataSource = dataSource as HikariDataSource
        val properties = hikariDataSource.dataSourceProperties

        assertNull(
            properties.getProperty("warehouse"),
            "Warehouse should not be set even with key pair authentication"
        )
        assertEquals(
            "rsa_key.p8_metadata",
            properties.getProperty("private_key_file"),
            "Metadata connection should use separate key file to avoid conflicts"
        )
    }

    @Test
    fun testBothConnectionsCanCoexist() {
        // Given: A standard Snowflake configuration
        val config = createTestConfig()

        // When: Creating both regular and metadata data sources
        val regularDataSource = SnowflakeDatabaseUtils.createDataSource(config, "test-env")
        val metadataDataSource = SnowflakeDatabaseUtils.createMetadataDataSource(config, "test-env")

        // Then: Both should be created successfully with different properties
        assertNotNull(regularDataSource)
        assertNotNull(metadataDataSource)

        val regularProps = (regularDataSource as HikariDataSource).dataSourceProperties
        val metadataProps = (metadataDataSource as HikariDataSource).dataSourceProperties

        // Regular connection has warehouse
        assertEquals("TEST_WAREHOUSE", regularProps.getProperty("warehouse"))
        assertEquals("test-env", regularProps.getProperty("application"))

        // Metadata connection doesn't have warehouse
        assertNull(metadataProps.getProperty("warehouse"))
        assertEquals("test-env-metadata", metadataProps.getProperty("application"))

        // Both share the same database and role
        assertEquals(
            regularProps.getProperty(JdbcUtils.DATABASE_KEY),
            metadataProps.getProperty(JdbcUtils.DATABASE_KEY)
        )
        assertEquals(regularProps.getProperty("role"), metadataProps.getProperty("role"))
    }

    private fun createTestConfig(): ObjectNode {
        val config = mapper.createObjectNode()
        config.put(JdbcUtils.HOST_KEY, "test-account.snowflakecomputing.com")
        config.put(JdbcUtils.USERNAME_KEY, "test_user")
        config.put(JdbcUtils.DATABASE_KEY, "TEST_DATABASE")
        config.put(JdbcUtils.SCHEMA_KEY, "TEST_SCHEMA")
        config.put("warehouse", "TEST_WAREHOUSE")
        config.put("role", "TEST_ROLE")

        val credentials = mapper.createObjectNode()
        credentials.put(JdbcUtils.PASSWORD_KEY, "test_password")
        config.set<ObjectNode>("credentials", credentials)

        return config
    }

    private fun createTestConfigWithOAuth(): ObjectNode {
        val config = mapper.createObjectNode()
        config.put(JdbcUtils.HOST_KEY, "test-account.snowflakecomputing.com")
        config.put(JdbcUtils.USERNAME_KEY, "test_user")
        config.put(JdbcUtils.DATABASE_KEY, "TEST_DATABASE")
        config.put(JdbcUtils.SCHEMA_KEY, "TEST_SCHEMA")
        config.put("warehouse", "TEST_WAREHOUSE")
        config.put("role", "TEST_ROLE")

        val credentials = mapper.createObjectNode()
        credentials.put("auth_type", "OAuth2.0")
        credentials.put("client_id", "test-client-id")
        credentials.put("client_secret", "test-client-secret")
        credentials.put("refresh_token", "test-refresh-token")
        config.set<ObjectNode>("credentials", credentials)

        return config
    }

    private fun createTestConfigWithKeyPair(): ObjectNode {
        val config = mapper.createObjectNode()
        config.put(JdbcUtils.HOST_KEY, "test-account.snowflakecomputing.com")
        config.put(JdbcUtils.USERNAME_KEY, "test_user")
        config.put(JdbcUtils.DATABASE_KEY, "TEST_DATABASE")
        config.put(JdbcUtils.SCHEMA_KEY, "TEST_SCHEMA")
        config.put("warehouse", "TEST_WAREHOUSE")
        config.put("role", "TEST_ROLE")

        val credentials = mapper.createObjectNode()
        credentials.put(
            "private_key",
            "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----"
        )
        credentials.put("private_key_password", "test_password")
        config.set<ObjectNode>("credentials", credentials)

        return config
    }
}
