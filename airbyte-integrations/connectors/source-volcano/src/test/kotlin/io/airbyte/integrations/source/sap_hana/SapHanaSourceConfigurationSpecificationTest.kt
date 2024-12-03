/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.sap_hana

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
class SapHanaSourceConfigurationSpecificationTest {
    @Inject
    lateinit var supplier:
        ConfigurationSpecificationSupplier<SapHanaSourceConfigurationSpecification>

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.schemas", value = "FOO,SYSTEM")
    @Property(
        name = "airbyte.connector.config.connection_data.connection_type",
        value = "service_name",
    )
    @Property(name = "airbyte.connector.config.connection_data.service_name", value = "FREEPDB1")
    @Property(name = "airbyte.connector.config.encryption.encryption_method", value = "client_nne")
    @Property(name = "airbyte.connector.config.encryption.encryption_algorithm", value = "3DES168")
    @Property(
        name = "airbyte.connector.config.tunnel_method.tunnel_method",
        value = "SSH_PASSWORD_AUTH",
    )
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_host", value = "localhost")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_port", value = "2222")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user", value = "sshuser")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user_password", value = "***")
    fun testPropertyInjection() {
        val pojo: SapHanaSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("localhost", pojo.host)
        Assertions.assertEquals(12345, pojo.port)
        Assertions.assertEquals("FOO", pojo.username)
        Assertions.assertEquals("BAR", pojo.password)
        Assertions.assertEquals(listOf("FOO", "SYSTEM"), pojo.schemas)
        val encryption: Encryption = pojo.getEncryptionValue()
        Assertions.assertTrue(encryption is EncryptionAlgorithm, encryption::class.toString())
        Assertions.assertEquals(
            "3DES168",
            (encryption as? EncryptionAlgorithm)?.encryptionAlgorithm,
        )
        val tunnelMethod: SshTunnelMethodConfiguration = pojo.getTunnelMethodValue()
        Assertions.assertTrue(
            tunnelMethod is SshPasswordAuthTunnelMethod,
            tunnelMethod::class.toString(),
        )
    }

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON)
    fun testJson() {
        val pojo: SapHanaSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("localhost", pojo.host)
        Assertions.assertEquals(12345, pojo.port)
        Assertions.assertEquals("FOO", pojo.username)
        Assertions.assertEquals("BAR", pojo.password)
        Assertions.assertEquals(listOf("FOO", "SYSTEM"), pojo.schemas)
        val encryption: Encryption = pojo.getEncryptionValue()
        Assertions.assertTrue(encryption is EncryptionAlgorithm, encryption::class.toString())
        Assertions.assertEquals(
            "3DES168",
            (encryption as? EncryptionAlgorithm)?.encryptionAlgorithm,
        )
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
  "connection_data": {
    "connection_type": "service_name",
    "service_name": "FREEPDB1"
  },
  "username": "FOO",
  "password": "BAR",
  "schemas": [
    "FOO",
    "SYSTEM"
  ],
  "encryption": {
    "encryption_method": "client_nne",
    "encryption_algorithm": "3DES168"
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
