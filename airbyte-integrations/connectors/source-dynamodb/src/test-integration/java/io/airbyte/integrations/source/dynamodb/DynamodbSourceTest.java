/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;

public class DynamodbSourceTest {

  private static final String TABLE_NAME = "airbyte_table";

  private DynamodbSource dynamodbSource;

  private DynamoDbClient dynamoDbClient;

  private DynamodbContainer dynamodbContainer;

  @BeforeEach
  void setup() {
    dynamodbContainer = DynamodbContainer.createWithStart();

    var jsonConfig = DynamodbDataFactory.createJsonConfig(dynamodbContainer);

    this.dynamodbSource = new DynamodbSource();
    this.dynamoDbClient = DynamodbUtils.createDynamoDbClient(DynamodbConfig.createDynamodbConfig(jsonConfig));

  }

  @AfterEach
  void shutdown() {
    dynamoDbClient.close();
    dynamodbContainer.stop();
    dynamodbContainer.close();
  }

  @Test
  void testCheckWithSucceeded() {

    var jsonConfig = DynamodbDataFactory.createJsonConfig(dynamodbContainer);

    DynamodbDataFactory.createTables(TABLE_NAME, 1).forEach(dynamoDbClient::createTable);

    var connectionStatus = dynamodbSource.check(jsonConfig);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.SUCCEEDED);

  }

  @Test
  void testCheckWithFailed() {

    var jsonConfig = DynamodbDataFactory.createJsonConfig(dynamodbContainer);
    ((ObjectNode) jsonConfig).replace("endpoint", Jsons.jsonNode("localhost:8080"));

    DynamodbDataFactory.createTables(TABLE_NAME, 1).forEach(dynamoDbClient::createTable);

    var connectionStatus = dynamodbSource.check(jsonConfig);

    assertThat(connectionStatus.getStatus()).isEqualTo(AirbyteConnectionStatus.Status.FAILED);

  }

  @Test
  void testDiscover() {

    var jsonConfig = DynamodbDataFactory.createJsonConfig(dynamodbContainer);

    var createTableRequests = DynamodbDataFactory.createTables(TABLE_NAME, 2);

    var createTableResponses = createTableRequests.stream().map(dynamoDbClient::createTable).toList();

    DynamodbDataFactory.putItemRequest(createTableResponses.get(0).tableDescription().tableName(), Map.of(
        "attr_1", AttributeValue.builder().s("str_4").build(),
        "attr_2", AttributeValue.builder().s("str_5").build(),
        "attr_3", AttributeValue.builder().s("2017-12-21T17:42:34Z").build(),
        "attr_4", AttributeValue.builder().ns("12.5", "74.5").build()));

    DynamodbDataFactory.putItemRequest(createTableResponses.get(1).tableDescription().tableName(), Map.of(
        "attr_1", AttributeValue.builder().s("str_4").build(),
        "attr_2", AttributeValue.builder().s("str_5").build(),
        "attr_4", AttributeValue.builder().s("2017-12-21T17:42:34Z").build(),
        "attr_5", AttributeValue.builder().ns("12.5", "74.5").build()));

    var airbyteCatalog = dynamodbSource.discover(jsonConfig);

    assertThat(airbyteCatalog.getStreams())
        .anyMatch(as -> as.getName().equals(createTableResponses.get(0).tableDescription().tableName()) &&
            as.getJsonSchema().isObject() &&
            as.getSourceDefinedPrimaryKey().get(0).containsAll(List.of("attr_1", "attr_2")) &&
            as.getSupportedSyncModes().containsAll(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)))
        .anyMatch(as -> as.getName().equals(createTableResponses.get(1).tableDescription().tableName()) &&
            as.getJsonSchema().isObject() &&
            as.getSourceDefinedPrimaryKey().get(0).containsAll(List.of("attr_1", "attr_2")) &&
            as.getSupportedSyncModes().containsAll(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL)));

  }

  @Test
  void testRead() {

    var jsonConfig = DynamodbDataFactory.createJsonConfig(dynamodbContainer);

    var createTableRequests = DynamodbDataFactory.createTables(TABLE_NAME, 1);
    var createTableResponses = createTableRequests.stream().map(dynamoDbClient::createTable).toList();
    String tableName = createTableResponses.get(0).tableDescription().tableName();
    var configuredCatalog = DynamodbDataFactory.createConfiguredAirbyteCatalog(tableName);

    PutItemRequest putItemRequest1 = DynamodbDataFactory.putItemRequest(tableName, Map.of(
        "attr_1", AttributeValue.builder().s("str_4").build(),
        "attr_2", AttributeValue.builder().s("str_5").build(),
        "attr_3", AttributeValue.builder().n("1234.25").build(),
        "attr_timestamp", AttributeValue.builder().n("1572268323").build()));

    dynamoDbClient.putItem(putItemRequest1);

    PutItemRequest putItemRequest2 = DynamodbDataFactory.putItemRequest(tableName, Map.of(
        "attr_1", AttributeValue.builder().s("str_6").build(),
        "attr_2", AttributeValue.builder().s("str_7").build(),
        "attr_3", AttributeValue.builder().n("1234.25").build(),
        "attr_timestamp", AttributeValue.builder().n("1672228343").build()));

    dynamoDbClient.putItem(putItemRequest2);

    Iterator<AirbyteMessage> iterator = dynamodbSource.read(jsonConfig, configuredCatalog, Jsons.emptyObject());

    var airbyteRecordMessages = Stream.generate(() -> null)
        .takeWhile(x -> iterator.hasNext())
        .map(n -> iterator.next())
        .filter(am -> am.getType() == AirbyteMessage.Type.RECORD)
        .map(AirbyteMessage::getRecord)
        .toList();

    assertThat(airbyteRecordMessages)
        .anyMatch(arm -> arm.getStream().equals(tableName) &&
            Jsons.serialize(arm.getData()).equals(
                "{\"attr_timestamp\":1572268323,\"attr_3\":1234.25,\"attr_2\":\"str_5\",\"attr_1\":\"str_4\"}"))
        .anyMatch(arm -> arm.getStream().equals(tableName) &&
            Jsons.serialize(arm.getData()).equals(
                "{\"attr_timestamp\":1672228343,\"attr_3\":1234.25,\"attr_2\":\"str_7\",\"attr_1\":\"str_6\"}"));

  }

}
