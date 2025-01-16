package io.airbyte.integrations.source.postgresv2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.command.ConfigurationSpecificationSupplier
import io.micronaut.context.annotation.Property
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class PostgresV2SourceConfigurationSpecificationTest {
    @Inject
    lateinit var supplier:
        ConfigurationSpecificationSupplier<PostgresV2SourceConfigurationSpecification>

    @Test
    @Property(name = "airbyte.connector.config.host", value = "localhost")
    @Property(name = "airbyte.connector.config.port", value = "12345")
    @Property(name = "airbyte.connector.config.username", value = "FOO")
    @Property(name = "airbyte.connector.config.password", value = "BAR")
    @Property(name = "airbyte.connector.config.database", value = "TESTDB")
    @Property(name = "airbyte.connector.config.schemas", value = "FOO,SYSTEM")
    fun testPropertyInjection() {
        val pojo: PostgresV2SourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("localhost", pojo.host)
        Assertions.assertEquals(12345, pojo.port)
        Assertions.assertEquals("FOO", pojo.username)
        Assertions.assertEquals("BAR", pojo.password)
        Assertions.assertEquals("TESTDB", pojo.database)
        Assertions.assertEquals(listOf("FOO", "SYSTEM"), pojo.schemas)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = CONFIG_JSON)
    fun testJson() {
        val pojo: PostgresV2SourceConfigurationSpecification = supplier.get()
        Assertions.assertEquals("localhost", pojo.host)
        Assertions.assertEquals(12345, pojo.port)
        Assertions.assertEquals("FOO", pojo.username)
        Assertions.assertEquals("BAR", pojo.password)
        Assertions.assertEquals(listOf("FOO", "SYSTEM"), pojo.schemas)
        Assertions.assertEquals("TESTDB", pojo.database)
    }
}

const val CONFIG_JSON =
    """
{
  "host": "localhost",
  "port": 12345,
  "database": "TESTDB",
  "username": "FOO",
  "password": "BAR",
  "schemas": [
    "FOO",
    "SYSTEM"
  ]
}
"""

