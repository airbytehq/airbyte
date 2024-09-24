/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.mysql

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationJsonObjectSupplier
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class MysqlSourceConfigurationJsonObjectTest {
    @Inject
    lateinit var supplier: ConfigurationJsonObjectSupplier<MysqlSourceConfigurationJsonObject>

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON)
    fun testJson() {
        val pojo: MysqlSourceConfigurationJsonObject = supplier.get()
        Assertions.assertEquals("localhost", pojo.host)
        Assertions.assertEquals(12345, pojo.port)
        Assertions.assertEquals("FOO", pojo.username)
        Assertions.assertEquals("BAR", pojo.password)
        Assertions.assertEquals(listOf("FOO", "SYSTEM"), pojo.schemas)
        val encryption: Encryption = pojo.getEncryptionValue()
        Assertions.assertTrue(encryption is EncryptionPreferred, encryption::class.toString())
        val tunnelMethod: SshTunnelMethodConfiguration = pojo.getTunnelMethodValue()
        Assertions.assertTrue(
            tunnelMethod is SshPasswordAuthTunnelMethod,
            tunnelMethod::class.toString(),
        )
        Assertions.assertEquals(60, pojo.checkpointTargetIntervalSeconds)
        Assertions.assertEquals(2, pojo.concurrency)
    }
}

const val CONFIG_JSON =
    """
{
  "host": "localhost",
  "port": 12345,
  "username": "FOO",
  "password": "BAR",
  "schemas": [
    "FOO",
    "SYSTEM"
  ],
  "encryption": {
    "encryption_method": "preferred"
  },
  "tunnel_method": {
    "tunnel_method": "SSH_PASSWORD_AUTH",
    "tunnel_host": "localhost",
    "tunnel_port": 2222,
    "tunnel_user": "sshuser",
    "tunnel_user_password": "***"
  },
  "cursor": {
    "cursor_method": "user_defined"
  },
  "checkpoint_target_interval_seconds": 60,
  "concurrency": 2
}
"""
