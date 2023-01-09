/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.json.JSONException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.skyscreamer.jsonassert.JSONAssert;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;

public class DynamodbOperationsTest {

  private static final String TABLE_NAME = "airbyte_table";

  private DynamodbOperations dynamodbOperations;

  private DynamoDbClient dynamoDbClient;

  private DynamodbContainer dynamodbContainer;

  private ObjectMapper objectMapper;

  @BeforeEach
  void setup() {
    dynamodbContainer = DynamodbContainer.createWithStart();

    var jsonConfig = DynamodbDataFactory.createJsonConfig(dynamodbContainer);

    this.dynamodbOperations = new DynamodbOperations(DynamodbConfig.createDynamodbConfig(jsonConfig));
    this.dynamoDbClient = DynamodbUtils.createDynamoDbClient(DynamodbConfig.createDynamodbConfig(jsonConfig));

    this.objectMapper = new ObjectMapper()
        .configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true)
        .configure(SerializationFeature.INDENT_OUTPUT, true);

  }

  @AfterEach
  void shutdown() {
    dynamoDbClient.close();
    dynamodbOperations.close();
    dynamodbContainer.stop();
    dynamodbContainer.close();
  }

  @Test
  void testListTables() {

    var createTableRequests = DynamodbDataFactory.createTables(TABLE_NAME, 5);
    createTableRequests.forEach(dynamoDbClient::createTable);

    List<String> tables = dynamodbOperations.listTables();

    assertThat(tables).hasSize(5)
        .anyMatch(t -> t.equals(TABLE_NAME + 1))
        .anyMatch(t -> t.equals(TABLE_NAME + 2))
        .anyMatch(t -> t.equals(TABLE_NAME + 3))
        .anyMatch(t -> t.equals(TABLE_NAME + 4))
        .anyMatch(t -> t.equals(TABLE_NAME + 5));

  }

  @Test
  void testPrimaryKey() {

    var createTableRequests = DynamodbDataFactory.createTables(TABLE_NAME, 1);
    var createTableResponse = dynamoDbClient.createTable(createTableRequests.get(0));

    var primaryKey = dynamodbOperations.primaryKey(createTableResponse.tableDescription().tableName());

    assertThat(primaryKey).hasSize(2)
        .anyMatch(t -> t.equals("attr_1"))
        .anyMatch(t -> t.equals("attr_2"));

  }

  @Test
  void testInferSchema() throws JsonProcessingException, JSONException {

    var createTableRequests = DynamodbDataFactory.createTables(TABLE_NAME, 1);
    var createTableResponse = dynamoDbClient.createTable(createTableRequests.get(0));
    String tableName = createTableResponse.tableDescription().tableName();

    PutItemRequest putItemRequest1 = DynamodbDataFactory.putItemRequest(tableName, Map.of(
        "attr_1", AttributeValue.builder().s("str_4").build(),
        "attr_2", AttributeValue.builder().s("str_5").build(),
        "attr_3", AttributeValue.builder().n("1234").build(),
        "attr_4", AttributeValue.builder().ns("12.5", "74.5").build()));

    dynamoDbClient.putItem(putItemRequest1);

    PutItemRequest putItemRequest2 = DynamodbDataFactory.putItemRequest(tableName, Map.of(
        "attr_1", AttributeValue.builder().s("str_6").build(),
        "attr_2", AttributeValue.builder().s("str_7").build(),
        "attr_5", AttributeValue.builder().bool(true).build(),
        "attr_6", AttributeValue.builder().ss("str_1", "str_2").build()));

    dynamoDbClient.putItem(putItemRequest2);

    var schema = dynamodbOperations.inferSchema(tableName, 1000);

    JSONAssert.assertEquals(objectMapper.writeValueAsString(schema), """
                                                                     {
                                                                     	"attr_5": {
                                                                     		"type": ["null","boolean"]
                                                                     	},
                                                                     	"attr_4": {
                                                                     		"type": ["null","array"],
                                                                     		"items": {
                                                                     			"type": ["null","number"]
                                                                     		}
                                                                     	},
                                                                     	"attr_3": {
                                                                     		"type": ["null","integer"]
                                                                     	},
                                                                     	"attr_2": {
                                                                     		"type": ["null","string"]
                                                                     	},
                                                                     	"attr_1": {
                                                                     		"type": ["null","string"]
                                                                     	},
                                                                     	"attr_6": {
                                                                     		"type": ["null","array"],
                                                                     		"items": {
                                                                     			"type": ["null","string"]
                                                                     		}
                                                                     	}
                                                                     }
                                                                     """, true);

  }

  @Test
  void testScanTable() throws JsonProcessingException, JSONException {

    var createTableRequests = DynamodbDataFactory.createTables(TABLE_NAME, 1);
    var createTableResponse = dynamoDbClient.createTable(createTableRequests.get(0));
    String tableName = createTableResponse.tableDescription().tableName();

    PutItemRequest putItemRequest1 = DynamodbDataFactory.putItemRequest(tableName, Map.of(
        "attr_1", AttributeValue.builder().s("str_4").build(),
        "attr_2", AttributeValue.builder().s("str_5").build(),
        "attr_3", AttributeValue.builder().s("2017-12-21T17:42:34Z").build(),
        "attr_4", AttributeValue.builder().ns("12.5", "74.5").build()));

    dynamoDbClient.putItem(putItemRequest1);

    PutItemRequest putItemRequest2 = DynamodbDataFactory.putItemRequest(tableName, Map.of(
        "attr_1", AttributeValue.builder().s("str_6").build(),
        "attr_2", AttributeValue.builder().s("str_7").build(),
        "attr_3", AttributeValue.builder().s("2019-12-21T17:42:34Z").build(),
        "attr_6", AttributeValue.builder().ss("str_1", "str_2").build()));

    dynamoDbClient.putItem(putItemRequest2);

    var response = dynamodbOperations.scanTable(tableName, Set.of("attr_1", "attr_2", "attr_3"),
        new DynamodbOperations.FilterAttribute("attr_3", "2018-12-21T17:42:34Z",
            DynamodbOperations.FilterAttribute.FilterType.S));

    assertThat(response)
        .hasSize(1);

    JSONAssert.assertEquals(objectMapper.writeValueAsString(response.get(0)), """
                                                                              {
                                                                              	"attr_3": "2019-12-21T17:42:34Z",
                                                                              	"attr_2": "str_7",
                                                                              	"attr_1": "str_6"
                                                                              }
                                                                              """, true);

  }

}
