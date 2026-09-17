/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import io.airbyte.cdk.ConfigErrorException
import io.airbyte.cdk.util.Jsons
import java.net.URI
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test
import software.amazon.awssdk.regions.Region

class DynamoDbSourceConfigurationFactoryTest {

    private fun parse(json: String): DynamoDbSourceConfigurationSpecification =
        Jsons.readValue(json, DynamoDbSourceConfigurationSpecification::class.java)

    private fun make(json: String): DynamoDbSourceConfiguration =
        DynamoDbSourceConfigurationFactory().makeWithoutExceptionHandling(parse(json))

    @Test
    fun testAccessKeyConfiguration() {
        val config: DynamoDbSourceConfiguration =
            make(
                """
{
  "credentials": {"auth_type": "User", "access_key_id": "AKIA123", "secret_access_key": "s3cr3t"},
  "endpoint": "http://localhost:8000",
  "region": "eu-west-1",
  "reserved_attribute_names": "name, field.name ,field-name,",
  "ignore_missing_read_permissions_tables": true
}
""",
            )
        Assertions.assertEquals("AKIA123", config.accessKeyId)
        Assertions.assertEquals("s3cr3t", config.secretAccessKey)
        Assertions.assertTrue(config.hasStaticCredentials)
        Assertions.assertEquals(URI.create("http://localhost:8000"), config.endpoint)
        Assertions.assertEquals(Region.EU_WEST_1, config.region)
        Assertions.assertEquals(
            listOf("name", "field.name", "field-name"),
            config.reservedAttributeNames
        )
        Assertions.assertTrue(config.ignoreMissingReadPermissionsTables)
        Assertions.assertEquals("localhost", config.realHost)
        Assertions.assertEquals(8000, config.realPort)
        Assertions.assertFalse(config.global)
        Assertions.assertEquals(1, config.maxConcurrency)
        Assertions.assertFalse(config.toString().contains("s3cr3t"), config.toString())
        Assertions.assertFalse(config.toString().contains("AKIA123"), config.toString())
    }

    @Test
    fun testRoleConfigurationDefaults() {
        val config: DynamoDbSourceConfiguration =
            make("""{"credentials": {"auth_type": "Role"}, "region": "us-east-1"}""")
        Assertions.assertNull(config.accessKeyId)
        Assertions.assertNull(config.secretAccessKey)
        Assertions.assertFalse(config.hasStaticCredentials)
        Assertions.assertNull(config.endpoint)
        Assertions.assertEquals(Region.US_EAST_1, config.region)
        Assertions.assertEquals(emptyList<String>(), config.reservedAttributeNames)
        Assertions.assertFalse(config.ignoreMissingReadPermissionsTables)
        Assertions.assertEquals("dynamodb.us-east-1.amazonaws.com", config.realHost)
        Assertions.assertEquals(443, config.realPort)
    }

    /** Legacy behavior: blank strings mean "not set" for endpoint, region and keys. */
    @Test
    fun testBlankValuesAreIgnored() {
        val config: DynamoDbSourceConfiguration =
            make(
                """
{
  "credentials": {"auth_type": "User", "access_key_id": "", "secret_access_key": " "},
  "endpoint": "",
  "region": "",
  "reserved_attribute_names": ""
}
""",
            )
        Assertions.assertFalse(config.hasStaticCredentials)
        Assertions.assertNull(config.endpoint)
        Assertions.assertNull(config.region)
        Assertions.assertEquals(emptyList<String>(), config.reservedAttributeNames)
        Assertions.assertEquals("dynamodb.amazonaws.com", config.realHost)
    }

    @Test
    fun testMissingCredentials() {
        val e: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make("""{"region": "us-east-1"}""")
            }
        Assertions.assertTrue(e.message!!.contains("credentials"), e.message)
        // The user-facing message must survive the factory's exception handling.
        val wrapped: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                DynamoDbSourceConfigurationFactory().make(parse("""{"region": "us-east-1"}"""))
            }
        Assertions.assertEquals(e.message, wrapped.message)
    }

    @Test
    fun testInvalidEndpoint() {
        val e: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                make("""{"credentials": {"auth_type": "Role"}, "endpoint": "http://bad host"}""")
            }
        Assertions.assertTrue(e.message!!.contains("Invalid endpoint"), e.message)
    }

    @Test
    fun testHostAndPort() {
        Assertions.assertEquals(
            "dynamodb-local" to 8000,
            DynamoDbSourceConfigurationFactory.hostAndPort(
                URI.create("http://dynamodb-local:8000"),
                null
            ),
        )
        Assertions.assertEquals(
            "vpce-123.dynamodb.us-east-1.vpce.amazonaws.com" to 443,
            DynamoDbSourceConfigurationFactory.hostAndPort(
                URI.create("https://vpce-123.dynamodb.us-east-1.vpce.amazonaws.com"),
                Region.US_EAST_1,
            ),
        )
        Assertions.assertEquals(
            "localhost" to 80,
            DynamoDbSourceConfigurationFactory.hostAndPort(URI.create("http://localhost"), null),
        )
    }
}
