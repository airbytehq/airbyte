/* Copyright (c) 2024 Airbyte, Inc., all rights reserved. */
package io.airbyte.cdk.command

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.fakesource.FakeSourceConfigurationSpecification
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.util.Jsons
import io.airbyte.cdk.util.ResourceUtils
import io.micronaut.context.annotation.Property
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(rebuildContext = true)
class ConfigurationSpecificationSupplierTest {
    @Inject
    lateinit var supplier: ConfigurationSpecificationSupplier<FakeSourceConfigurationSpecification>

    @Test
    fun testSchema() {
        Assertions.assertEquals(
            FakeSourceConfigurationSpecification::class.java,
            supplier.javaClass
        )
        val expected: String = ResourceUtils.readResource("fakesource/expected-schema.json")
        Assertions.assertEquals(Jsons.readTree(expected), supplier.jsonSchema)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "hello")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    fun testPropertyInjection() {
        val pojo: FakeSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("hello", pojo.host)
        Assertions.assertEquals("testdb", pojo.database)
        Assertions.assertEquals(SshNoTunnelMethod, pojo.getTunnelMethodValue())
    }

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(
        name = "airbyte.connector.config.json",
        value = """{"host":"hello","port":123,"database":"testdb"}""",
    )
    fun testGoodJson() {
        val pojo: FakeSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("hello", pojo.host)
        Assertions.assertEquals(123, pojo.port)
        Assertions.assertEquals("testdb", pojo.database)
        Assertions.assertEquals(SshNoTunnelMethod, pojo.getTunnelMethodValue())
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = """{"foo""")
    fun testMalformedJson() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(name = "airbyte.connector.config.host", value = "hello")
    @Property(name = "airbyte.connector.config.database", value = "testdb")
    @Property(
        name = "airbyte.connector.config.tunnel_method.tunnel_method",
        value = "SSH_PASSWORD_AUTH",
    )
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_host", value = "localhost")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_port", value = "22")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user", value = "sshuser")
    @Property(
        name = "airbyte.connector.config.tunnel_method.tunnel_user_password",
        value = "secret",
    )
    fun testPropertySubTypeInjection() {
        val pojo: FakeSourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("hello", pojo.host)
        Assertions.assertEquals("testdb", pojo.database)
        val expected = SshPasswordAuthTunnelMethod("localhost", 22, "sshuser", "secret")
        Assertions.assertEquals(expected, pojo.getTunnelMethodValue())
    }
}
