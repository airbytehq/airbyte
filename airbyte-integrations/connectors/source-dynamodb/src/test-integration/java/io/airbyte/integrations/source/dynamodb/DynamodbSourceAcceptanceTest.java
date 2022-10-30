/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.standardtest.source.SourceAcceptanceTest;
import io.airbyte.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import software.amazon.awssdk.services.dynamodb.model.AttributeDefinition;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.CreateTableRequest;
import software.amazon.awssdk.services.dynamodb.model.KeySchemaElement;
import software.amazon.awssdk.services.dynamodb.model.KeyType;
import software.amazon.awssdk.services.dynamodb.model.ProvisionedThroughput;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType;
import software.amazon.awssdk.services.dynamodb.model.TableClass;

public class DynamodbSourceAcceptanceTest extends SourceAcceptanceTest {

    private JsonNode config;

    private DynamodbContainer dynamodbContainer;

    private static final String TABLE_NAME = "airbyte_table";

    @Override
    protected void setupEnvironment(final TestDestinationEnv testEnv) {
        dynamodbContainer = DynamodbContainer.initWithStart();

        config = Jsons.jsonNode(ImmutableMap.builder()
            .put("dynamodb_endpoint", dynamodbContainer.getEndpointOverride().toString())
            .put("dynamodb_region", dynamodbContainer.getRegion())
            .put("access_key_id", dynamodbContainer.getAccessKey())
            .put("secret_access_key", dynamodbContainer.getSecretKey())
            .build());

        try (var dynamoDbClient = DynamodbUtils.initDynamoDbClient(DynamodbConfig.initConfigFromJson(config));) {

            CreateTableRequest createTableRequest = CreateTableRequest
                .builder()
                .tableClass(TableClass.STANDARD)
                .tableName(TABLE_NAME)
                .attributeDefinitions(
                    AttributeDefinition.builder()
                        .attributeName("attr_1")
                        .attributeType(ScalarAttributeType.S)
                        .build(),
                    AttributeDefinition.builder()
                        .attributeName("attr_2")
                        .attributeType(ScalarAttributeType.S)
                        .build()
                )
                .keySchema(
                    KeySchemaElement.builder()
                        .attributeName("attr_1")
                        .keyType(KeyType.HASH)
                        .build(),
                    KeySchemaElement.builder()
                        .attributeName("attr_2")
                        .keyType(KeyType.RANGE)
                        .build()
                )
                .provisionedThroughput(ProvisionedThroughput.builder()
                    .readCapacityUnits(10L)
                    .writeCapacityUnits(10L).build())
                .build();

            dynamoDbClient.createTable(createTableRequest);

            PutItemRequest putItemRequest = PutItemRequest
                .builder()
                .tableName(TABLE_NAME)
                .item(
                    Map.of(
                        "attr_1", AttributeValue.builder().s("str_4").build(),
                        "attr_2", AttributeValue.builder().s("str_5").build(),
                        "attr_3", AttributeValue.builder().n("1234.25").build(),
                        "attr_timestamp", AttributeValue.builder().n("14732908123").build())
                )
                .build();

            dynamoDbClient.putItem(putItemRequest);

        }
    }

    @Override
    protected void tearDown(final TestDestinationEnv testEnv) {
        dynamodbContainer.stop();
        dynamodbContainer.close();
    }

    @Override
    protected String getImageName() {
        return "airbyte/source-dynamodb:dev";
    }

    @Override
    protected ConnectorSpecification getSpec() throws Exception {
        return Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);
    }

    @Override
    protected JsonNode getConfig() {
        return config;
    }

    @Override
    protected ConfiguredAirbyteCatalog getConfiguredCatalog() throws IOException {
        return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
            new ConfiguredAirbyteStream()
                .withSyncMode(SyncMode.INCREMENTAL)
                .withCursorField(Lists.newArrayList("attr_timestamp"))
                .withPrimaryKey(List.of(List.of("attr_1", "attr_2")))
                .withDestinationSyncMode(DestinationSyncMode.APPEND)
                .withStream(CatalogHelpers.createAirbyteStream(
                        TABLE_NAME,
                        Field.of("attr_1", JsonSchemaType.STRING),
                        Field.of("attr_2", JsonSchemaType.STRING),
                        Field.of("attr_3", JsonSchemaType.NUMBER),
                        Field.of("attr_timestamp", JsonSchemaType.INTEGER))
                    .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
    }

    @Override
    protected JsonNode getState() {
        return Jsons.jsonNode(new HashMap<>());
    }

}
