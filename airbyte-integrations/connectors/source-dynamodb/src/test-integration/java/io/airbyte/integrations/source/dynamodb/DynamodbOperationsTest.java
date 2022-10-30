package io.airbyte.integrations.source.dynamodb;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.IntStream;
import org.json.JSONException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.skyscreamer.jsonassert.JSONAssert;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeDefinition;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.CreateTableRequest;
import software.amazon.awssdk.services.dynamodb.model.CreateTableResponse;
import software.amazon.awssdk.services.dynamodb.model.KeySchemaElement;
import software.amazon.awssdk.services.dynamodb.model.KeyType;
import software.amazon.awssdk.services.dynamodb.model.ProvisionedThroughput;
import software.amazon.awssdk.services.dynamodb.model.PutItemRequest;
import software.amazon.awssdk.services.dynamodb.model.ScalarAttributeType;
import software.amazon.awssdk.services.dynamodb.model.TableClass;

public class DynamodbOperationsTest {

    private static final String TABLE_NAME = "airbyte_table";

    private DynamodbOperations dynamodbOperations;

    private DynamoDbClient dynamoDbClient;

    private DynamodbContainer dynamodbContainer;

    private ObjectMapper objectMapper;

    @BeforeEach
    void setup() {
        dynamodbContainer = DynamodbContainer.initWithStart();

        var jsonConfig = Jsons.jsonNode(ImmutableMap.builder()
            .put("dynamodb_endpoint", dynamodbContainer.getEndpointOverride().toString())
            .put("dynamodb_region", dynamodbContainer.getRegion())
            .put("access_key_id", dynamodbContainer.getAccessKey())
            .put("secret_access_key", dynamodbContainer.getSecretKey())
            .build());

        this.dynamodbOperations = new DynamodbOperations(DynamodbConfig.initConfigFromJson(jsonConfig));
        this.dynamoDbClient = DynamodbUtils.initDynamoDbClient(DynamodbConfig.initConfigFromJson(jsonConfig));

        this.objectMapper = new ObjectMapper()
            .configure(SerializationFeature.ORDER_MAP_ENTRIES_BY_KEYS, true)
            .configure(SerializationFeature.INDENT_OUTPUT, true);

    }

    @AfterEach
    void shutdown() {
        dynamoDbClient.close();
        dynamodbOperations.close();
        dynamodbContainer.stop();
        dynamodbOperations.close();
    }

    @Test
    void testListTables() {

        createTables(5);

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

        var createTableResponses = createTables(1);

        var primaryKey = dynamodbOperations.primaryKey(createTableResponses.get(0).tableDescription().tableName());

        assertThat(primaryKey).hasSize(2)
            .anyMatch(t -> t.equals("attr_1"))
            .anyMatch(t -> t.equals("attr_2"));

    }

    @Test
    void testInferSchema() throws JsonProcessingException, JSONException {

        var createTableResponses = createTables(1);
        String tableName = createTableResponses.get(0).tableDescription().tableName();

        PutItemRequest putItemRequest1 = PutItemRequest
            .builder()
            .tableName(tableName)
            .item(
                Map.of(
                    "attr_1", AttributeValue.builder().s("str_4").build(),
                    "attr_2", AttributeValue.builder().s("str_5").build(),
                    "attr_3", AttributeValue.builder().n("1234").build(),
                    "attr_4", AttributeValue.builder().ns("12.5", "74.5").build())
            )
            .build();

        dynamoDbClient.putItem(putItemRequest1);

        PutItemRequest putItemRequest2 = PutItemRequest
            .builder()
            .tableName(tableName)
            .item(
                Map.of(
                    "attr_1", AttributeValue.builder().s("str_6").build(),
                    "attr_2", AttributeValue.builder().s("str_7").build(),
                    "attr_5", AttributeValue.builder().bool(true).build(),
                    "attr_6", AttributeValue.builder().ss("str_1", "str_2").build())
            )
            .build();

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

        var createTableResponses = createTables(1);
        String tableName = createTableResponses.get(0).tableDescription().tableName();

        PutItemRequest putItemRequest1 = PutItemRequest
            .builder()
            .tableName(tableName)
            .item(
                Map.of(
                    "attr_1", AttributeValue.builder().s("str_4").build(),
                    "attr_2", AttributeValue.builder().s("str_5").build(),
                    "attr_3", AttributeValue.builder().s("2017-12-21T17:42:34Z").build(),
                    "attr_4", AttributeValue.builder().ns("12.5", "74.5").build())
            )
            .build();

        dynamoDbClient.putItem(putItemRequest1);

        PutItemRequest putItemRequest2 = PutItemRequest
            .builder()
            .tableName(tableName)
            .item(
                Map.of(
                    "attr_1", AttributeValue.builder().s("str_6").build(),
                    "attr_2", AttributeValue.builder().s("str_7").build(),
                    "attr_3", AttributeValue.builder().s("2019-12-21T17:42:34Z").build(),
                    "attr_6", AttributeValue.builder().ss("str_1", "str_2").build())
            )
            .build();

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

    private List<CreateTableResponse> createTables(int tables) {
        List<CreateTableResponse> createTableResponses = new ArrayList<>();
        IntStream.range(0, tables).mapToObj(range -> CreateTableRequest
                .builder()
                .tableClass(TableClass.STANDARD)
                .tableName(TABLE_NAME + (range + 1))
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
                .build())
            .map(dynamoDbClient::createTable)
            .forEach(createTableResponses::add);
        return createTableResponses;
    }


}
