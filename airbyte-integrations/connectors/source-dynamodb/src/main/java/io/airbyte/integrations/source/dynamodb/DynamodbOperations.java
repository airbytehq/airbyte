/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.dynamodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import io.airbyte.cdk.db.AbstractDatabase;
import java.io.Closeable;
import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.dynamodb.model.AttributeDefinition;
import software.amazon.awssdk.services.dynamodb.model.AttributeValue;
import software.amazon.awssdk.services.dynamodb.model.DescribeTableRequest;
import software.amazon.awssdk.services.dynamodb.model.ListTablesRequest;
import software.amazon.awssdk.services.dynamodb.model.ListTablesResponse;
import software.amazon.awssdk.services.dynamodb.model.ScanRequest;

public class DynamodbOperations extends AbstractDatabase implements Closeable {

  private final DynamoDbClient dynamoDbClient;

  private ObjectMapper attributeObjectMapper;

  private ObjectMapper schemaObjectMapper;

  private DynamodbConfig dynamodbConfig;

  public DynamodbOperations(DynamodbConfig dynamodbConfig) {
    this.dynamodbConfig = dynamodbConfig;
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
    List<String> tableNames = new ArrayList<>();
    ListTablesRequest listTablesRequest = ListTablesRequest.builder().build();
    boolean completed = false;

    while (!completed) {
      ListTablesResponse listTablesResponse = dynamoDbClient.listTables(listTablesRequest);
      tableNames.addAll(listTablesResponse.tableNames());

      if (listTablesResponse.lastEvaluatedTableName() == null) {
        completed = true;
      } else {
        listTablesRequest = listTablesRequest.toBuilder()
            .exclusiveStartTableName(listTablesResponse.lastEvaluatedTableName())
            .build();
      }
    }

    return tableNames;
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

      // can scan a 'bit' more items than 'sampleSize' if response is > 1MB since every
      // new page request on the iterator will return new 'sampleSize' amount of items.
      scannedItems += scanResponse.count();

      items.addAll(scanResponse.items());

    }

    /*
     * schema inference with combining only the top level attributes of different items. for complete
     * schema inference the implementation should do full traversal of each item object graph and merge
     * different nested attributes at the same level
     */
    Map<String, AttributeValue> mergedItems = items.stream()
        .reduce(new HashMap<>(), (merged, current) -> {
          merged.putAll(current);
          return merged;
        });

    return schemaObjectMapper.convertValue(mergedItems, JsonNode.class);
  }

  public List<JsonNode> scanTable(String tableName, Set<String> attributes, FilterAttribute filterAttribute) {
    List<JsonNode> items = new ArrayList<>();

    String prefix = "dyndb";
    // remove and replace reserved attribute names
    Set<String> copyAttributes = new HashSet<>(attributes);
    dynamodbConfig.reservedAttributeNames().forEach(copyAttributes::remove);
    dynamodbConfig.reservedAttributeNames().stream()
        .filter(attributes::contains)
        .map(str -> str.replaceAll("[-.]", ""))
        .forEach(attr -> copyAttributes.add("#" + prefix + "_" + attr));

    Map<String, String> mappingAttributes = dynamodbConfig.reservedAttributeNames().stream()
        .filter(attributes::contains)
        .collect(Collectors.toUnmodifiableMap(k -> "#" + prefix + "_" + k.replaceAll("[-.]", ""), k -> k));

    var projectionAttributes = String.join(", ", copyAttributes);

    ScanRequest.Builder scanRequestBuilder = ScanRequest.builder()
        .tableName(tableName)
        .projectionExpression(projectionAttributes);

    if (!mappingAttributes.isEmpty()) {
      scanRequestBuilder
          .expressionAttributeNames(mappingAttributes);
    }

    if (filterAttribute != null && filterAttribute.name() != null &&
        filterAttribute.value() != null && filterAttribute.type() != null) {

      var filterName = filterAttribute.name();
      var filterValue = filterAttribute.value();

      // Dynamodb supports timestamp filtering based on ISO format as string and Epoch format as number
      // type
      AttributeValue attributeValue = switch (filterAttribute.type()) {
        case S -> AttributeValue.builder().s(filterValue).build();
        case N -> AttributeValue.builder().n(filterValue).build();
      };

      String comparator;
      try {
        // if date is of format 2016-02-15 we should use gr-eq in order to not skip records
        // from the same date after first replication
        LocalDate.parse(filterValue);
        comparator = ">=";
      } catch (DateTimeParseException e) {
        comparator = ">";
      }

      String filterPlaceholder =
          dynamodbConfig.reservedAttributeNames().contains(filterName) ? "#" + prefix + "_" + filterName.replaceAll("[-.]", "") : filterName;
      scanRequestBuilder
          .filterExpression(filterPlaceholder + " " + comparator + " :timestamp")
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

      S,
      N

    }

  }

}
