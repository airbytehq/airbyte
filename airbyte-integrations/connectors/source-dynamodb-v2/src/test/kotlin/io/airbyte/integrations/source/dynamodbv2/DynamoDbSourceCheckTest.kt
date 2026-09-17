/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.integrations.source.dynamodbv2.DynamoDbLocalContainer.Companion.createTableWithItems
import java.io.File
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assumptions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.KeyType
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType

/** Runs the CHECK operation against real DynamoDB Local containers. */
class DynamoDbSourceCheckTest {

    @Test
    fun testCheckSucceedsWithAccessKeys() {
        SyncsTestFixture.testCheck(seeded.config())
    }

    /**
     * Role-based access picks credentials up from the SDK default chain, here system properties.
     */
    @Test
    fun testCheckSucceedsWithRoleBasedAccess() {
        withSystemProperties(
            mapOf(
                "aws.accessKeyId" to DynamoDbLocalContainer.ACCESS_KEY_ID,
                "aws.secretAccessKey" to DynamoDbLocalContainer.SECRET_ACCESS_KEY,
            ),
        ) {
            SyncsTestFixture.testCheck(seeded.config(accessKeyId = null, secretAccessKey = null))
        }
    }

    /** Legacy behavior: blank keys fall back to the default chain, like role-based access. */
    @Test
    fun testCheckSucceedsWithBlankAccessKeys() {
        withSystemProperties(
            mapOf(
                "aws.accessKeyId" to DynamoDbLocalContainer.ACCESS_KEY_ID,
                "aws.secretAccessKey" to DynamoDbLocalContainer.SECRET_ACCESS_KEY,
            ),
        ) {
            SyncsTestFixture.testCheck(seeded.config(accessKeyId = "", secretAccessKey = ""))
        }
    }

    @Test
    fun testCheckSucceedsWithReservedAttributeNamesAndIgnoreFlag() {
        SyncsTestFixture.testCheck(
            seeded.config(
                extra =
                    mapOf(
                        "reserved_attribute_names" to "name, field.name, field-name",
                        "ignore_missing_read_permissions_tables" to true,
                    ),
            ),
        )
    }

    @Test
    fun testCheckFailsWithoutTables() {
        SyncsTestFixture.testCheck(empty.config(), expectedFailure = "Discovered zero tables")
    }

    @Test
    fun testCheckFailsWhenUnreachable() {
        SyncsTestFixture.testCheck(
            DynamoDbLocalContainer.parseConfig(
                mapOf(
                    "credentials" to
                        mapOf(
                            "auth_type" to "User",
                            "access_key_id" to "local",
                            "secret_access_key" to "local",
                        ),
                    "endpoint" to "http://localhost:1",
                    "region" to DynamoDbLocalContainer.REGION,
                ),
            ),
            expectedFailure = "Could not reach the DynamoDB endpoint",
        )
    }

    @Test
    fun testCheckFailsWithoutCredentialsProperty() {
        SyncsTestFixture.testCheck(
            DynamoDbLocalContainer.parseConfig(
                mapOf("endpoint" to seeded.endpoint.toString(), "region" to "us-east-1"),
            ),
            expectedFailure = "Missing required 'credentials' property",
        )
    }

    /** Only meaningful on a machine without ambient AWS credentials. */
    @Test
    fun testCheckFailsWithRoleBasedAccessWithoutAmbientCredentials() {
        Assumptions.assumeTrue(
            System.getenv().keys.none { it.startsWith("AWS_") } &&
                !File(System.getProperty("user.home"), ".aws/credentials").exists(),
            "ambient AWS credentials present",
        )
        SyncsTestFixture.testCheck(
            seeded.config(accessKeyId = null, secretAccessKey = null),
            expectedFailure = "No AWS credentials found",
        )
    }

    companion object {
        lateinit var seeded: DynamoDbLocalContainer
        lateinit var empty: DynamoDbLocalContainer

        @JvmStatic
        @BeforeAll
        fun startContainers() {
            seeded = DynamoDbLocalContainer().also { it.start() }
            empty = DynamoDbLocalContainer().also { it.start() }
            seeded.client().use { client ->
                client.createTableWithItems(
                    "people",
                    listOf(KeyElement("id", KeyType.HASH, ScalarAttributeType.S)),
                    listOf(
                        mapOf(
                            "id" to AttributeValue.builder().s("1").build(),
                            "name" to AttributeValue.builder().s("alice").build(),
                        ),
                    ),
                )
            }
        }

        @JvmStatic
        @AfterAll
        fun stopContainers() {
            seeded.stop()
            empty.stop()
        }

        fun withSystemProperties(properties: Map<String, String>, block: () -> Unit) {
            val previous: Map<String, String?> =
                properties.keys.associateWith { System.getProperty(it) }
            properties.forEach { (k, v) -> System.setProperty(k, v) }
            try {
                block()
            } finally {
                previous.forEach { (k, v) ->
                    if (v == null) System.clearProperty(k) else System.setProperty(k, v)
                }
            }
        }
    }
}
