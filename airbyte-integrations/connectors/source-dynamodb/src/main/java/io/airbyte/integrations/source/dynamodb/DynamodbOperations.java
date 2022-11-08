package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import io.airbyte.db.AbstractDatabase;
import java.io.Closeable;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeDefinition;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.DescribeTableRequest;
import software.amazon.awssdk.services.dynamodb.model.ScanRequest;

public class DynamodbOperations extends AbstractDatabase implements Closeable {

    private final DynamoDbClient dynamoDbClient;

    private ObjectMapper attributeObjectMapper;

    private ObjectMapper schemaObjectMapper;

    public DynamodbOperations(DynamodbConfig dynamodbConfig) {
        this.dynamoDbClient = DynamodbUtils.createDynamoDbClient(dynamodbConfig);
        initMappers();
    }

    public DynamodbOperations(DynamoDbClient dynamoDbClient) {
        this.dynamoDbClient = dynamoDbClient;
        initMappers();
    }

    private void initMappers() {
        SimpleModule attributeModule = new SimpleModule();
        attributeModule.addSerializer(AttributeValue.class, new DynamodbAttributeSerializer());
        this.attributeObjectMapper = new ObjectMapper().registerModule(attributeModule);

        SimpleModule schemaModule = new SimpleModule();
        schemaModule.addSerializer(AttributeValue.class, new DynamodbSchemaSerializer());
        this.schemaObjectMapper = new ObjectMapper().registerModule(schemaModule);
    }

    public List<String> listTables() {
        return dynamoDbClient.listTables()
            // filter on table status?
            .tableNames();
    }

    public List<String> primaryKey(String tableName) {
        DescribeTableRequest describeTableRequest = DescribeTableRequest.builder().tableName(tableName).build();
        return dynamoDbClient.describeTable(describeTableRequest).table().attributeDefinitions().stream()
            .map(AttributeDefinition::attributeName)
            .toList();
    }

    public JsonNode inferSchema(String tableName, int sampleSize) {

        List<Map<String, AttributeValue>> items = new ArrayList<>();

        ScanRequest scanRequest = ScanRequest.builder()
            .limit(sampleSize)
            .tableName(tableName)
            .build();

        var scanIterable = dynamoDbClient.scanPaginator(scanRequest);
        int scannedItems = 0;
        for (var scanResponse : scanIterable) {

            if (scannedItems >= sampleSize) {
                break;
            }

            // TODO(itaseski) will scan more items than specified my doing them in batch of sampleSize
            scannedItems += scanResponse.count();

            items.addAll(scanResponse.items());

        }

        /*
         * naive schema inference with combining only the top level attributes of different items.
         * for better schema inference the implementation should do full traversal of each item object graph
         * and merge different nested attributes at each level
         * */
        Map<String, AttributeValue> mergedItems = items.stream()
            .reduce(new HashMap<>(), (merged, current) -> {
                merged.putAll(current);
                return merged;
            });

        return schemaObjectMapper.convertValue(mergedItems, JsonNode.class);
    }

    public List<JsonNode> scanTable(String tableName, Set<String> attributes, FilterAttribute filterAttribute) {
        List<JsonNode> items = new ArrayList<>();

        var projectionAttributes = String.join(", ", attributes);

        ScanRequest.Builder scanRequestBuilder = ScanRequest.builder()
            .tableName(tableName)
            .projectionExpression(projectionAttributes);

        if (filterAttribute != null && filterAttribute.name() != null &&
            filterAttribute.value() != null && filterAttribute.type() != null) {

            var filterName = filterAttribute.name();
            var filterValue = filterAttribute.value();

            // Dynamodb supports timestamp filtering based on ISO format as string and Epoch format as number type
            AttributeValue attributeValue = switch (filterAttribute.type()) {
                case S -> AttributeValue.builder().s(filterValue).build();
                case N -> AttributeValue.builder().n(filterValue).build();
            };

            scanRequestBuilder
                // flawed approach when syncing data with the ISO format 2016-02-15 since
                // once records for that date are synced additional syncs will ignore new records from the same date
                .filterExpression(filterName + " > :timestamp")
                .expressionAttributeValues(Map.of(":timestamp", attributeValue));

        }

        var scanIterable = dynamoDbClient.scanPaginator(scanRequestBuilder.build());
        for (var scanResponse : scanIterable) {

            scanResponse.items().stream()
                .map(attr -> attributeObjectMapper.convertValue(attr, JsonNode.class))
                .forEach(items::add);

        }

        return items;
    }

    @Override
    public void close() {
        dynamoDbClient.close();
    }


    public record FilterAttribute(String name, String value, FilterType type) {

        public enum FilterType {

            S, N

        }

    }


}
