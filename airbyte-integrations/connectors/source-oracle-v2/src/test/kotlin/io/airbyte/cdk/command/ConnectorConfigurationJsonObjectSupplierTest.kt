package io.airbyte.cdk.command

import com.fasterxml.jackson.annotation.JsonGetter
import com.fasterxml.jackson.annotation.JsonIgnore
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonSetter
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaDefault
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.ssh.MicronautPropertiesFriendlySshTunnelMethodConfigurationJsonObject
import io.airbyte.cdk.ssh.SshNoTunnelMethod
import io.airbyte.cdk.ssh.SshPasswordAuthTunnelMethod
import io.airbyte.cdk.ssh.SshTunnelMethodConfiguration
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import io.micronaut.context.annotation.Primary
import io.micronaut.context.annotation.Property
import io.micronaut.context.annotation.Requires
import io.micronaut.context.env.Environment
import io.micronaut.test.extensions.junit5.annotation.MicronautTest
import jakarta.inject.Inject
import jakarta.inject.Singleton
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

@MicronautTest(environments = [Environment.TEST], rebuildContext = true)
class ConnectorConfigurationJsonObjectSupplierTest {

    @Inject lateinit var supplier: ConnectorConfigurationJsonObjectSupplier<TestingJsonObject>

    @Test
    fun testSchema() {
        Assertions.assertEquals(TestingJsonObject::class.java, supplier.valueClass)
        Assertions.assertEquals(Jsons.deserialize(EXPECTED_JSON_SCHEMA), supplier.jsonSchema)
    }

    @Test
    @Property(name = "airbyte.connector.config.foo", value = "hello")
    fun testPropertyInjection() {
        val pojo: TestingJsonObject = supplier.get()
        Assertions.assertEquals("hello", pojo.foo)
        Assertions.assertEquals(123, pojo.bar)
        Assertions.assertEquals(SshNoTunnelMethod, pojo.getTunnelMethod())
    }

    @Test
    fun testSchemaViolation() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = """{"foo":"hello"}""")
    fun testGoodJson() {
        val pojo: TestingJsonObject = supplier.get()
        Assertions.assertEquals("hello", pojo.foo)
        Assertions.assertEquals(123, pojo.bar)
        Assertions.assertEquals(SshNoTunnelMethod, pojo.getTunnelMethod())
    }

    @Test
    @Property(name = "airbyte.connector.config.json", value = """{"foo""")
    fun testMalformedJson() {
        Assertions.assertThrows(ConfigErrorException::class.java, supplier::get)
    }

    @Test
    @Property(name = "airbyte.connector.config.foo", value = "hello")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_method", value = "SSH_PASSWORD_AUTH")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_host", value = "localhost")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_port", value = "22")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user", value = "sshuser")
    @Property(name = "airbyte.connector.config.tunnel_method.tunnel_user_password", value = "secret")
    fun testPropertySubTypeInjection() {
        val pojo: TestingJsonObject = supplier.get()
        Assertions.assertEquals("hello", pojo.foo)
        Assertions.assertEquals(123, pojo.bar)
        val expected = SshPasswordAuthTunnelMethod("localhost", 22, "sshuser", "secret")
        Assertions.assertEquals(expected, pojo.getTunnelMethod())
    }
}

@JsonSchemaTitle("Fake connector configuration")
@Singleton
@Requires(env = [Environment.TEST])
@Requires(bean = ConnectorConfigurationJsonObjectSupplierTest::class)
@Primary
@ConfigurationProperties(CONNECTOR_CONFIG_PREFIX)
class TestingJsonObject : ConnectorConfigurationJsonObjectBase() {

    @JsonProperty("foo", required = true)
    var foo: String? = null

    @JsonProperty("bar")
    @JsonSchemaDefault("123")
    var bar: Int? = 123

    @JsonIgnore
    @ConfigurationBuilder(configurationPrefix = "tunnel_method")
    val tunnelMethod = MicronautPropertiesFriendlySshTunnelMethodConfigurationJsonObject()

    @JsonIgnore
    var tunnelMethodJson: SshTunnelMethodConfiguration? = null

    @JsonSetter("tunnel_method")
    fun setTunnelMethod(value: SshTunnelMethodConfiguration) {
        tunnelMethodJson = value
    }

    @JsonGetter("tunnel_method")
    fun getTunnelMethod(): SshTunnelMethodConfiguration =
        tunnelMethodJson ?: tunnelMethod.asSshTunnelMethod()
}

const val EXPECTED_JSON_SCHEMA = """
{
  "${'$'}schema": "http://json-schema.org/draft-07/schema#",
  "title": "Fake connector configuration",
  "type": "object",
  "additionalProperties": true,
  "properties": {
    "foo": {
      "type": "string"
    },
    "bar": {
      "type": "integer",
      "default": 123
    },
    "tunnel_method": {
      "oneOf": [
        {
          "${'$'}ref": "#/definitions/SshNoTunnelMethod",
          "title": "No Tunnel"
        },
        {
          "${'$'}ref": "#/definitions/SshKeyAuthTunnelMethod",
          "title": "SSH Key Authentication"
        },
        {
          "${'$'}ref": "#/definitions/SshPasswordAuthTunnelMethod",
          "title": "Password Authentication"
        }
      ]
    }
  },
  "required": [
    "foo"
  ],
  "definitions": {
    "SshNoTunnelMethod": {
      "type": "object",
      "additionalProperties": true,
      "description": "No ssh tunnel needed to connect to database",
      "title": "NO_TUNNEL",
      "properties": {
        "tunnel_method": {
          "type": "string",
          "enum": [
            "NO_TUNNEL"
          ],
          "default": "NO_TUNNEL"
        }
      },
      "required": [
        "tunnel_method"
      ]
    },
    "SshKeyAuthTunnelMethod": {
      "type": "object",
      "additionalProperties": true,
      "description": "Connect through a jump server tunnel host using username and ssh key",
      "title": "SSH_KEY_AUTH",
      "properties": {
        "tunnel_method": {
          "type": "string",
          "enum": [
            "SSH_KEY_AUTH"
          ],
          "default": "SSH_KEY_AUTH"
        },
        "tunnel_host": {
          "type": "string",
          "description": "Hostname of the jump server host that allows inbound ssh tunnel.",
          "title": "SSH Tunnel Jump Server Host",
          "order": 1
        },
        "tunnel_port": {
          "type": "integer",
          "default": 22,
          "description": "Port on the proxy/jump server that accepts inbound ssh connections.",
          "title": "SSH Connection Port",
          "order": 2,
          "minimum": 0,
          "maximum": 65536
        },
        "tunnel_user": {
          "type": "string",
          "description": "OS-level username for logging into the jump server host",
          "title": "SSH Login Username",
          "order": 3
        },
        "ssh_key": {
          "type": "string",
          "description": "OS-level user account ssh key credentials in RSA PEM format ( created with ssh-keygen -t rsa -m PEM -f myuser_rsa )",
          "title": "SSH Private Key",
          "order": 4,
          "multiline": true,
          "airbyte_secret": true
        }
      },
      "required": [
        "tunnel_method",
        "tunnel_host",
        "tunnel_port",
        "tunnel_user",
        "ssh_key"
      ]
    },
    "SshPasswordAuthTunnelMethod": {
      "type": "object",
      "additionalProperties": true,
      "description": "Connect through a jump server tunnel host using username and password authentication",
      "title": "SSH_PASSWORD_AUTH",
      "properties": {
        "tunnel_method": {
          "type": "string",
          "enum": [
            "SSH_PASSWORD_AUTH"
          ],
          "default": "SSH_PASSWORD_AUTH"
        },
        "tunnel_host": {
          "type": "string",
          "description": "Hostname of the jump server host that allows inbound ssh tunnel.",
          "title": "SSH Tunnel Jump Server Host",
          "order": 1
        },
        "tunnel_port": {
          "type": "integer",
          "default": 22,
          "description": "Port on the proxy/jump server that accepts inbound ssh connections.",
          "title": "SSH Connection Port",
          "order": 2,
          "minimum": 0,
          "maximum": 65536
        },
        "tunnel_user": {
          "type": "string",
          "description": "OS-level username for logging into the jump server host",
          "title": "SSH Login Username",
          "order": 3
        },
        "tunnel_user_password": {
          "type": "string",
          "description": "OS-level password for logging into the jump server host",
          "title": "Password",
          "order": 4,
          "airbyte_secret": true
        }
      },
      "required": [
        "tunnel_method",
        "tunnel_host",
        "tunnel_port",
        "tunnel_user",
        "tunnel_user_password"
      ]
    }
  }
}
"""
