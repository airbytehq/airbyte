/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.Map;
import java.util.stream.IntStream;
import software.amazon.awssdk.services.dynamodb.model.AttributeDefinition;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.CreateTableRequest;
import software.amazon.awssdk.services.dynamodb.model.KeySchemaElement;
import software.amazon.awssdk.services.dynamodb.model.KeyType;
import software.amazon.awssdk.services.dynamodb.model.ProvisionedThroughput;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType;
import software.amazon.awssdk.services.dynamodb.model.TableClass;

public class DynamodbDataFactory {

  private DynamodbDataFactory() {

  }

  public static List<CreateTableRequest> createTables(String tablePrefix, int tables) {
    return IntStream.range(0, tables).mapToObj(range -> CreateTableRequest
        .builder()
        .tableClass(TableClass.STANDARD)
        .tableName(tablePrefix + (range + 1))
        .attributeDefinitions(
            AttributeDefinition.builder()
                .attributeName("attr_1")
                .attributeType(ScalarAttributeType.S)
                .build(),
            AttributeDefinition.builder()
                .attributeName("attr_2")
                .attributeType(ScalarAttributeType.S)
                .build())
        .keySchema(
            KeySchemaElement.builder()
                .attributeName("attr_1")
                .keyType(KeyType.HASH)
                .build(),
            KeySchemaElement.builder()
                .attributeName("attr_2")
                .keyType(KeyType.RANGE)
                .build())
        .provisionedThroughput(ProvisionedThroughput.builder()
            .readCapacityUnits(10L)
            .writeCapacityUnits(10L).build())
        .build())
        .toList();

  }

  public static PutItemRequest putItemRequest(String tableName, Map<String, AttributeValue> item) {
    return PutItemRequest
        .builder()
        .tableName(tableName)
        .item(item)
        .build();

  }

  public static JsonNode createJsonConfig(DynamodbContainer dynamodbContainer) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("endpoint", dynamodbContainer.getEndpointOverride().toString())
        .put("region", dynamodbContainer.getRegion())
        .put("access_key_id", dynamodbContainer.getAccessKey())
        .put("secret_access_key", dynamodbContainer.getSecretKey())
        .build());
  }

  public static ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(String streamName) {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withCursorField(Lists.newArrayList("attr_timestamp"))
            .withPrimaryKey(List.of(List.of("attr_1", "attr_2")))
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(CatalogHelpers.createAirbyteStream(
                streamName,
                Field.of("attr_1", JsonSchemaType.STRING),
                Field.of("attr_2", JsonSchemaType.STRING),
                Field.of("attr_3", JsonSchemaType.NUMBER),
                Field.of("attr_timestamp", JsonSchemaType.INTEGER))
                .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))));
  }

}
