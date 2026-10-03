/* Copyright (c) 2026 Airbyte, Inc., all rights reserved. */
package io.airbyte.integrations.source.dynamodbv2

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.util.Jsons
import java.net.URI
import org.testcontainers.containers.GenericContainer
import org.testcontainers.utility.DockerImageName
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider
import software.amazon.awssdk.regions.Region
import software.amazon.awssdk.services.dynamodb.DynamoDbClient
import software.amazon.awssdk.services.dynamodb.model.AttributeDefinition
import software.amazon.awssdk.services.dynamodb.model.AttributeValue
import software.amazon.awssdk.services.dynamodb.model.BatchWriteItemRequest
import software.amazon.awssdk.services.dynamodb.model.BatchWriteItemResponse
import software.amazon.awssdk.services.dynamodb.model.BillingMode
import software.amazon.awssdk.services.dynamodb.model.CreateTableRequest
import software.amazon.awssdk.services.dynamodb.model.KeySchemaElement
import software.amazon.awssdk.services.dynamodb.model.KeyType
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest
import software.amazon.awssdk.services.dynamodb.model.PutRequest
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType
import software.amazon.awssdk.services.dynamodb.model.WriteRequest

/**
 * The official `amazon/dynamodb-local` image (no Testcontainers module exists for it). It accepts
 * any access key; `-sharedDb` makes the tables visible regardless of the key and region used.
 */
class DynamoDbLocalContainer :
    GenericContainer<DynamoDbLocalContainer>(DockerImageName.parse(IMAGE)) {

    init {
        withExposedPorts(PORT)
        withCommand("-jar", "DynamoDBLocal.jar", "-inMemory", "-sharedDb")
    }

    val endpoint: URI
        get() = URI.create("http://$host:${getMappedPort(PORT)}")

    fun client(): DynamoDbClient =
        DynamoDbClient.builder()
            .endpointOverride(endpoint)
            .region(Region.of(REGION))
            .credentialsProvider(
                StaticCredentialsProvider.create(
                    AwsBasicCredentials.create(ACCESS_KEY_ID, SECRET_ACCESS_KEY)
                ),
            )
            .build()

    /** Connector configuration pointing at this container, with (dummy) access key credentials. */
    fun config(
        accessKeyId: String = ACCESS_KEY_ID,
        secretAccessKey: String = SECRET_ACCESS_KEY,
        extra: Map<String, Any?> = emptyMap(),
    ): DynamoDbSourceConfigurationSpecification =
        parseConfig(
            mapOf(
                "credentials" to
                    mapOf(
                        "auth_type" to "User",
                        "access_key_id" to accessKeyId,
                        "secret_access_key" to secretAccessKey,
                    ),
                "endpoint" to endpoint.toString(),
                "region" to REGION,
            ) + extra,
        )

    companion object {
        const val IMAGE = "amazon/dynamodb-local:3.3.1"
        const val PORT = 8000
        const val REGION = "us-east-1"
        /** DynamoDB Local accepts any access key; these are the AWS documentation examples. */
        const val ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
        const val SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

        fun parseConfig(config: Map<String, Any?>): DynamoDbSourceConfigurationSpecification =
            Jsons.readValue(
                Jsons.writeValueAsString(config),
                DynamoDbSourceConfigurationSpecification::class.java,
            )

        /** Creates a table with the given key schema and puts the items. */
        fun DynamoDbClient.createTableWithItems(
            tableName: String,
            keySchema: List<KeyElement>,
            items: List<Map<String, AttributeValue>>,
        ) {
            createTable(
                CreateTableRequest.builder()
                    .tableName(tableName)
                    .billingMode(BillingMode.PAY_PER_REQUEST)
                    .keySchema(
                        keySchema.map {
                            KeySchemaElement.builder()
                                .attributeName(it.attributeName)
                                .keyType(it.keyType)
                                .build()
                        },
                    )
                    .attributeDefinitions(
                        keySchema.map {
                            AttributeDefinition.builder()
                                .attributeName(it.attributeName)
                                .attributeType(it.attributeType)
                                .build()
                        },
                    )
                    .build(),
            )
            for (item in items) {
                putItem(PutItemRequest.builder().tableName(tableName).item(item).build())
            }
        }

        /** Parses an attribute value in DynamoDB JSON (`{"S": "x"}`, `{"N": "1"}`, ...). */
        fun attributeValue(node: JsonNode): AttributeValue = DynamoDbJson.fromDynamoDbJson(node)

        /** Parses an item in DynamoDB JSON: attribute name to typed value. */
        fun item(node: JsonNode): Map<String, AttributeValue> =
            DynamoDbJson.itemFromDynamoDbJson(node)

        /** Writes items 25 at a time (the `BatchWriteItem` maximum). */
        fun DynamoDbClient.batchPutItems(
            tableName: String,
            items: List<Map<String, AttributeValue>>,
        ) {
            for (chunk: List<Map<String, AttributeValue>> in items.chunked(25)) {
                var pending: Map<String, List<WriteRequest>> =
                    mapOf(
                        tableName to
                            chunk.map {
                                WriteRequest.builder()
                                    .putRequest(PutRequest.builder().item(it).build())
                                    .build()
                            },
                    )
                while (pending.isNotEmpty()) {
                    val response: BatchWriteItemResponse =
                        batchWriteItem(
                            BatchWriteItemRequest.builder().requestItems(pending).build()
                        )
                    pending =
                        if (response.hasUnprocessedItems()) response.unprocessedItems()
                        else emptyMap()
                }
            }
        }
    }
}

data class KeyElement(
    val attributeName: String,
    val keyType: KeyType,
    val attributeType: ScalarAttributeType,
)
