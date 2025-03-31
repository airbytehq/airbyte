/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MySqlSourceConfigurationSpecificationTest {

    @Inject
    lateinit var supplier: ConfigurationSpecificationSupplier<MySqlSourceConfigurationSpecification>

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON)
    fun testJson() {
        val pojo: MySqlSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("localhost", pojo.host)
        Assertions.assertEquals(12345, pojo.port)
        Assertions.assertEquals("FOO", pojo.username)
        Assertions.assertEquals("BAR", pojo.password)
        Assertions.assertEquals("SYSTEM", pojo.database)
        val encryption: EncryptionSpecification = pojo.getEncryptionValue()!!
        Assertions.assertTrue(encryption is EncryptionPreferred, encryption::class.toString())
        val tunnelMethod: SshTunnelMethodConfiguration? = pojo.getTunnelMethodValue()
        Assertions.assertTrue(
            tunnelMethod is SshPasswordAuthTunnelMethod,
            tunnelMethod!!::class.toString(),
        )
        Assertions.assertEquals(60, pojo.checkpointTargetIntervalSeconds)
        Assertions.assertEquals(2, pojo.concurrency)
    }

    /**
     * Verifies that the encryption mode is correctly set to "required" as the default value in the
     * MySqlSourceConfigurationSpecification class.
     */
    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON_ENCRYPTION_CHECK)
    fun testDefaultEncryption() {
        val pojo: MySqlSourceConfigurationSpecification = supplier.get()
        val encryption: EncryptionSpecification = pojo.getEncryptionValue()!!
        Assertions.assertTrue(encryption is EncryptionRequired, encryption::class.toString())
    }

    companion object {

        const val CONFIG_JSON: String =
            """
{
  "host": "localhost",
  "port": 12345,
  "username": "FOO",
  "password": "BAR",
  "database": "SYSTEM",
  "ssl_mode": {
    "mode": "preferred"
  },
  "tunnel_method": {
    "tunnel_method": "SSH_PASSWORD_AUTH",
    "tunnel_host": "localhost",
    "tunnel_port": 2222,
    "tunnel_user": "sshuser",
    "tunnel_user_password": "***"
  },
  "replication_method": {
    "method": "STANDARD"
  },
  "checkpoint_target_interval_seconds": 60,
  "jdbc_url_params": "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&",
  "concurrency": 2
}
"""

        const val CONFIG_JSON_ENCRYPTION_CHECK: String =
            """
{
  "host": "localhost",
  "port": 12345,
  "username": "FOO",
  "password": "BAR",
  "database": "SYSTEM",
  "tunnel_method": {
    "tunnel_method": "SSH_PASSWORD_AUTH",
    "tunnel_host": "localhost",
    "tunnel_port": 2222,
    "tunnel_user": "sshuser",
    "tunnel_user_password": "***"
  },
  "replication_method": {
    "method": "STANDARD"
  },
  "checkpoint_target_interval_seconds": 60,
  "jdbc_url_params": "theAnswerToLiveAndEverything=42&sessionVariables=max_execution_time=10000&foo=bar&",
  "concurrency": 2
}
"""
    }
}
