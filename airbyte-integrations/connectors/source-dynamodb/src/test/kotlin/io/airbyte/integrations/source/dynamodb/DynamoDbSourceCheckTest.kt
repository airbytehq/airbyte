/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import io.airbyte.cdk.command.SyncsTestFixture
import io.airbyte.integrations.source.dynamodb.DynamoDbLocalContainer.Companion.createTableWithItems
import org.junit.jupiter.api.AfterAll
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

    /** DynamoDB Local ignores the session token, but the SDK still signs with it. */
    @Test
    fun testCheckSucceedsWithTemporaryCredentials() {
        SyncsTestFixture.testCheck(
            seeded.config(
                extra =
                    mapOf(
                        "credentials" to
                            mapOf(
                                "auth_type" to "User",
                                "access_key_id" to DynamoDbLocalContainer.ACCESS_KEY_ID,
                                "secret_access_key" to DynamoDbLocalContainer.SECRET_ACCESS_KEY,
                                "session_token" to "FwoGZXIvYXdzEBYaDEXAMPLESESSIONTOKEN",
                            ),
                    ),
            ),
        )
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
            seeded.config(extra = mapOf("endpoint" to "http://localhost:1")),
            expectedFailure = "Could not reach the DynamoDB endpoint",
        )
    }

    @Test
    fun testCheckFailsWithBlankAccessKey() {
        SyncsTestFixture.testCheck(
            seeded.config(accessKeyId = ""),
            expectedFailure = "'access_key_id' property must not be blank",
        )
    }

    @Test
    fun testCheckFailsWithoutRegion() {
        SyncsTestFixture.testCheck(
            seeded.config(extra = mapOf("region" to "")),
            expectedFailure = "'region' property is required",
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
    }
}
