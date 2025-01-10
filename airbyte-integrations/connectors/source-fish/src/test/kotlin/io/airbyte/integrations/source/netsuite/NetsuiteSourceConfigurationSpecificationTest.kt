/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.netsuite

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class NetsuiteSourceConfigurationSpecificationTest {
    @Inject
    lateinit var supplier:
        ConfigurationSpecificationSupplier<NetsuiteSourceConfigurationSpecification>

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
        val pojo: NetsuiteSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("localhost", pojo.host)
        Assertions.assertEquals(12345, pojo.port)
        Assertions.assertEquals("FOO", pojo.username)
        Assertions.assertEquals("BAR", pojo.password)
    }

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }
}
