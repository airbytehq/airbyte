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

    private fun assertConfigError(json: String, expectedMessagePart: String) {
        val e: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) { make(json) }
        Assertions.assertTrue(e.message!!.contains(expectedMessagePart), e.message)
        // The user-facing message must survive the factory's exception handling.
        val wrapped: ConfigErrorException =
            Assertions.assertThrows(ConfigErrorException::class.java) {
                DynamoDbSourceConfigurationFactory().make(parse(json))
            }
        Assertions.assertEquals(e.message, wrapped.message)
    }

    @Test
    fun testAccessKeyConfiguration() {
        val config: DynamoDbSourceConfiguration =
            make(
                """
{
  "credentials": {"auth_type": "User", "access_key_id": " AKIA123 ", "secret_access_key": "s3cr3t", "session_token": "tok"},
  "endpoint": "http://localhost:8000",
  "region": "eu-west-1",
  "reserved_attribute_names": "name, field.name ,field-name,",
  "ignore_missing_read_permissions_tables": true
}
""",
            )
        Assertions.assertEquals("AKIA123", config.accessKeyId)
        Assertions.assertEquals("s3cr3t", config.secretAccessKey)
        Assertions.assertEquals("tok", config.sessionToken)
        Assertions.assertNull(config.roleArn)
        Assertions.assertFalse(config.assumesRole)
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
        for (secret in listOf("AKIA123", "s3cr3t", "tok")) {
            Assertions.assertFalse(config.toString().contains(secret), config.toString())
        }
    }

    @Test
    fun testAssumeRoleConfiguration() {
        val config: DynamoDbSourceConfiguration =
            make(
                """
{
  "credentials": {
    "auth_type": "AssumeRole",
    "access_key_id": "AKIA123",
    "secret_access_key": "s3cr3t",
    "role_arn": "arn:aws:iam::123456789012:role/path/airbyte-reader",
    "external_id": "ext-123"
  },
  "region": "us-east-1"
}
""",
            )
        Assertions.assertTrue(config.assumesRole)
        Assertions.assertEquals(
            "arn:aws:iam::123456789012:role/path/airbyte-reader",
            config.roleArn
        )
        Assertions.assertEquals("ext-123", config.externalId)
        Assertions.assertNull(config.sessionToken)
        Assertions.assertNull(config.endpoint)
        Assertions.assertEquals("dynamodb.us-east-1.amazonaws.com", config.realHost)
        Assertions.assertEquals(443, config.realPort)
        Assertions.assertFalse(config.toString().contains("ext-123"), config.toString())
    }

    @Test
    fun testDefaults() {
        val config: DynamoDbSourceConfiguration =
            make(
                """{"credentials": {"auth_type": "User", "access_key_id": "k", "secret_access_key": "s"}, "region": "us-gov-west-1", "endpoint": "  "}""",
            )
        Assertions.assertNull(config.sessionToken)
        Assertions.assertNull(config.endpoint)
        Assertions.assertEquals(Region.US_GOV_WEST_1, config.region)
        Assertions.assertEquals(emptyList<String>(), config.reservedAttributeNames)
        Assertions.assertFalse(config.ignoreMissingReadPermissionsTables)
    }

    @Test
    fun testMissingCredentials() {
        assertConfigError("""{"region": "us-east-1"}""", "Missing required 'credentials' property")
    }

    /**
     * The legacy `Role` variant (SDK default credentials chain) is rejected with a clear message.
     */
    @Test
    fun testLegacyRoleBasedAuthenticationIsRejected() {
        assertConfigError(
            """{"credentials": {"auth_type": "Role"}, "region": "us-east-1"}""",
            "Role based authentication",
        )
        assertConfigError(
            """{"credentials": {"auth_type": "Whatever"}, "region": "us-east-1"}""",
            "Unsupported credentials type",
        )
    }

    @Test
    fun testBlankAccessKeys() {
        assertConfigError(
            """{"credentials": {"auth_type": "User", "access_key_id": "", "secret_access_key": "s"}, "region": "us-east-1"}""",
            "'access_key_id' property must not be blank",
        )
        assertConfigError(
            """{"credentials": {"auth_type": "User", "access_key_id": "k", "secret_access_key": " "}, "region": "us-east-1"}""",
            "'secret_access_key' property must not be blank",
        )
    }

    @Test
    fun testMissingRegion() {
        val credentials =
            """{"auth_type": "User", "access_key_id": "k", "secret_access_key": "s"}"""
        assertConfigError("""{"credentials": $credentials}""", "'region' property is required")
        assertConfigError(
            """{"credentials": $credentials, "region": ""}""",
            "'region' property is required"
        )
    }

    @Test
    fun testInvalidRoleArn() {
        for (arn in listOf("", "reader", "arn:aws:iam::123:role/reader", "arn:aws:s3:::bucket")) {
            val e: ConfigErrorException =
                Assertions.assertThrows(ConfigErrorException::class.java) {
                    make(
                        """
{
  "credentials": {"auth_type": "AssumeRole", "access_key_id": "k", "secret_access_key": "s", "role_arn": "$arn"},
  "region": "us-east-1"
}
""",
                    )
                }
            Assertions.assertTrue(
                e.message!!.contains("role_arn") || e.message!!.contains("IAM role ARN"),
                e.message
            )
        }
    }

    @Test
    fun testInvalidEndpoint() {
        val credentials =
            """{"auth_type": "User", "access_key_id": "k", "secret_access_key": "s"}"""
        for (endpoint in
            listOf(
                "http://bad host",
                "localhost:8000",
                "ftp://host",
                "dynamodb.us-east-1.amazonaws.com"
            )) {
            assertConfigError(
                """{"credentials": $credentials, "region": "us-east-1", "endpoint": "$endpoint"}""",
                "Invalid endpoint",
            )
        }
    }

    @Test
    fun testHostAndPort() {
        Assertions.assertEquals(
            "dynamodb-local" to 8000,
            DynamoDbSourceConfigurationFactory.hostAndPort(
                URI.create("http://dynamodb-local:8000"),
                Region.US_EAST_1,
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
            DynamoDbSourceConfigurationFactory.hostAndPort(
                URI.create("http://localhost"),
                Region.US_EAST_1
            ),
        )
        Assertions.assertEquals(
            "dynamodb.cn-north-1.amazonaws.com" to 443,
            DynamoDbSourceConfigurationFactory.hostAndPort(null, Region.CN_NORTH_1),
        )
    }
}
