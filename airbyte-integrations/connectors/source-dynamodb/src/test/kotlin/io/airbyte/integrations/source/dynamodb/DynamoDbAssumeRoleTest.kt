/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodb

import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.source.dynamodb.DynamoDbLocalContainer.Companion.createTableWithItems
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.localstack.LocalStackContainer
import org.testcontainers.utility.DockerImageName
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.AwsSessionCredentials
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.dynamodb.DynamoDbClient
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.KeyType
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType

/**
 * Exercises the `sts:AssumeRole` credentials path against LocalStack, which emulates STS (any role
 * ARN is assumable and yields temporary credentials) and DynamoDB.
 */
class DynamoDbAssumeRoleTest {

    @Test
    fun testAssumedRoleCredentialsAreTemporary() {
        val provider =
            DynamoDbClientFactory.credentialsProvider(
                configuration(),
                stsEndpointOverride = localstack.endpoint,
            )
        val credentials = provider.resolveCredentials()
        Assertions.assertInstanceOf(AwsSessionCredentials::class.java, credentials)
        Assertions.assertNotEquals(localstack.accessKey, credentials.accessKeyId())
    }

    @Test
    fun testListTablesWithAssumedRole() {
        val client: DynamoDbClient =
            DynamoDbClientFactory.create(configuration(), stsEndpointOverride = localstack.endpoint)
        client.use {
            val querier = DynamoDbSourceMetadataQuerier(configuration(), it)
            Assertions.assertEquals(listOf(TABLE), querier.listTables())
            Assertions.assertEquals(
                listOf(listOf("id")),
                querier.primaryKey(querier.streamNames(null).single())
            )
        }
    }

    companion object {
        const val TABLE = "assumed"
        const val ROLE_ARN = "arn:aws:iam::000000000000:role/airbyte-dynamodb-reader"

        lateinit var localstack: LocalStackContainer

        @JvmStatic
        @BeforeAll
        fun startContainer() {
            localstack =
                LocalStackContainer(DockerImageName.parse("localstack/localstack:4.4.0"))
                    .withServices(
                        LocalStackContainer.Service.STS,
                        LocalStackContainer.Service.DYNAMODB
                    )
                    .also { it.start() }
            DynamoDbClient.builder()
                .endpointOverride(localstack.endpoint)
                .region(Region.of(localstack.region))
                .credentialsProvider(
                    StaticCredentialsProvider.create(
                        AwsBasicCredentials.create(localstack.accessKey, localstack.secretKey)
                    ),
                )
                .build()
                .use { client ->
                    client.createTableWithItems(
                        TABLE,
                        listOf(KeyElement("id", KeyType.HASH, ScalarAttributeType.S)),
                        listOf(mapOf("id" to AttributeValue.builder().s("1").build())),
                    )
                }
        }

        @JvmStatic
        @AfterAll
        fun stopContainer() {
            localstack.stop()
        }

        fun configuration(): DynamoDbSourceConfiguration =
            DynamoDbSourceConfigurationFactory()
                .make(
                    Jsons.readValue(
                        Jsons.writeValueAsString(
                            mapOf(
                                "credentials" to
                                    mapOf(
                                        "auth_type" to "AssumeRole",
                                        "access_key_id" to localstack.accessKey,
                                        "secret_access_key" to localstack.secretKey,
                                        "role_arn" to ROLE_ARN,
                                        "external_id" to "airbyte-external-id",
                                    ),
                                "region" to localstack.region,
                                "endpoint" to localstack.endpoint.toString(),
                            ),
                        ),
                        DynamoDbSourceConfigurationSpecification::class.java,
                    ),
                )
    }
}
