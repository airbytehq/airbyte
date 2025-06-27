/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.snowflake

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class SnowflakeSourceConfigurationSpecificationTest {

    @Inject
    lateinit var supplier:
        ConfigurationSpecificationSupplier<SnowflakeSourceConfigurationSpecification>

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON)
    fun testJson() {
        val pojo: SnowflakeSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("myaccount-region.snowflakecomputing.com", pojo.host)
        Assertions.assertEquals("ROLE_NAME", pojo.role)
        Assertions.assertEquals("WAREHOUSE_NAME", pojo.warehouse)
        Assertions.assertEquals("DATABASE_NAME", pojo.database)
        Assertions.assertEquals("SCHEMA_NAME", pojo.schema)
        Assertions.assertEquals("key1=value1&key2=value2", pojo.jdbcUrlParams)
        Assertions.assertEquals(300, pojo.checkpointTargetIntervalSeconds)
        Assertions.assertEquals(2, pojo.concurrency)
        Assertions.assertEquals(true, pojo.checkPrivileges)
        val credentials: CredentialsSpecification = pojo.credentials!!
        Assertions.assertTrue(
            credentials is UsernamePasswordCredentialsSpecification,
            credentials::class.toString()
        )
        val usernamePasswordCreds = credentials as UsernamePasswordCredentialsSpecification
        Assertions.assertEquals("TEST_USER", usernamePasswordCreds.username)
        Assertions.assertEquals("TEST_PASSWORD", usernamePasswordCreds.password)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_KEY_PAIR)
    fun testJsonKeyPairAuth() {
        val pojo: SnowflakeSourceConfigurationSpecification = supplier.get()
        val credentials: CredentialsSpecification = pojo.credentials!!
        Assertions.assertTrue(
            credentials is KeyPairCredentialsSpecification,
            credentials::class.toString()
        )
        val keyPairCreds = credentials as KeyPairCredentialsSpecification
        Assertions.assertEquals("TEST_USER", keyPairCreds.username)
        Assertions.assertEquals(
            "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----",
            keyPairCreds.privateKey
        )
        Assertions.assertEquals("passphrase123", keyPairCreds.privateKeyPassword)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_MINIMAL)
    fun testJsonMinimal() {
        val pojo: SnowflakeSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("myaccount-region.snowflakecomputing.com", pojo.host)
        Assertions.assertEquals("ROLE_NAME", pojo.role)
        Assertions.assertEquals("WAREHOUSE_NAME", pojo.warehouse)
        Assertions.assertEquals("DATABASE_NAME", pojo.database)
        Assertions.assertNull(pojo.schema)
        Assertions.assertNull(pojo.jdbcUrlParams)
        Assertions.assertEquals(300, pojo.checkpointTargetIntervalSeconds)
        Assertions.assertEquals(1, pojo.concurrency)
        Assertions.assertEquals(true, pojo.checkPrivileges)
    }

    companion object {

        const val CONFIG_JSON: String =
            """
{
  "credentials": {
    "auth_type": "username/password",
    "username": "TEST_USER",
    "password": "TEST_PASSWORD"
  },
  "host": "myaccount-region.snowflakecomputing.com",
  "role": "ROLE_NAME",
  "warehouse": "WAREHOUSE_NAME",
  "database": "DATABASE_NAME",
  "schema": "SCHEMA_NAME",
  "jdbc_url_params": "key1=value1&key2=value2",
  "cursor": {
    "cursor_method": "user_defined"
  },
  "checkpoint_target_interval_seconds": 300,
  "concurrency": 2,
  "check_privileges": true
}
"""

        const val CONFIG_JSON_KEY_PAIR: String =
            """
{
  "credentials": {
    "auth_type": "Key Pair Authentication",
    "username": "TEST_USER",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----",
    "private_key_password": "passphrase123"
  },
  "host": "myaccount-region.snowflakecomputing.com",
  "role": "ROLE_NAME",
  "warehouse": "WAREHOUSE_NAME",
  "database": "DATABASE_NAME",
  "schema": "SCHEMA_NAME",
  "cursor": {
    "cursor_method": "user_defined"
  }
}
"""

        const val CONFIG_JSON_MINIMAL: String =
            """
{
  "credentials": {
    "auth_type": "username/password",
    "username": "TEST_USER",
    "password": "TEST_PASSWORD"
  },
  "host": "myaccount-region.snowflakecomputing.com",
  "role": "ROLE_NAME",
  "warehouse": "WAREHOUSE_NAME",
  "database": "DATABASE_NAME"
}
"""
    }
}
