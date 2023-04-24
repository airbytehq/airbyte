/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import com.amazonaws.services.glue.AWSGlue;
import com.amazonaws.services.glue.model.Column;
import com.amazonaws.services.glue.model.CreateTableRequest;
import com.amazonaws.services.glue.model.DeleteTableRequest;
import com.amazonaws.services.glue.model.EntityNotFoundException;
import com.amazonaws.services.glue.model.GetTableRequest;
import com.amazonaws.services.glue.model.SerDeInfo;
import com.amazonaws.services.glue.model.StorageDescriptor;
import com.amazonaws.services.glue.model.TableInput;
import com.amazonaws.services.glue.model.UpdateTableRequest;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.base.Preconditions;
import java.util.Collection;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

// TODO (itaseski) implement wrapper for retry logic on transient errors
public class GlueOperations implements MetastoreOperations {

  private final ObjectMapper objectMapper;

  private final AWSGlue awsGlueClient;

  public GlueOperations(AWSGlue awsGlueClient) {
    Preconditions.checkArgument(awsGlueClient != null);
    this.awsGlueClient = awsGlueClient;
    this.objectMapper = new ObjectMapper();
  }

  @Override
  public void upsertTable(String databaseName,
                          String tableName,
                          String location,
                          JsonNode jsonSchema,
                          String serializationLibrary) {
    try {
      GetTableRequest getTableRequest = new GetTableRequest()
          .withDatabaseName(databaseName)
          .withName(tableName);

      // Will throw EntityNotFoundException if table doesn't exist
      awsGlueClient.getTable(getTableRequest);

      UpdateTableRequest updateTableRequest = new UpdateTableRequest()
          .withDatabaseName(databaseName)
          .withTableInput(
              new TableInput()
                  .withName(tableName)
                  .withTableType("EXTERNAL_TABLE")
                  .withStorageDescriptor(
                      new StorageDescriptor()
                          .withLocation(location)
                          .withColumns(transformSchema(jsonSchema))
                          .withInputFormat("org.apache.hadoop.mapred.TextInputFormat")
                          .withOutputFormat("org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat")
                          .withSerdeInfo(
                              new SerDeInfo()
                                  .withSerializationLibrary(serializationLibrary)
                                  .withParameters(Map.of("paths", ",")))

                  )
                  .withPartitionKeys(List.of())
                  .withParameters(Map.of("classification", "json")));

      awsGlueClient.updateTable(updateTableRequest);
    } catch (EntityNotFoundException enfe) {
      CreateTableRequest createTableRequest = new CreateTableRequest()
          .withDatabaseName(databaseName)
          .withTableInput(
              new TableInput()
                  .withName(tableName)
                  .withTableType("EXTERNAL_TABLE")
                  .withStorageDescriptor(
                      new StorageDescriptor()
                          .withLocation(location)
                          .withColumns(transformSchema(jsonSchema))
                          .withInputFormat("org.apache.hadoop.mapred.TextInputFormat")
                          .withOutputFormat("org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat")
                          .withSerdeInfo(
                              new SerDeInfo()
                                  .withSerializationLibrary(serializationLibrary)
                                  .withParameters(Map.of("paths", ","))))
                  .withPartitionKeys(List.of())
                  .withParameters(Map.of("classification", "json")));

      awsGlueClient.createTable(createTableRequest);
    }
  }

  @Override
  public void deleteTable(String databaseName, String tableName) {

    DeleteTableRequest deleteTableRequest = new DeleteTableRequest()
        .withDatabaseName(databaseName)
        .withName(tableName);

    awsGlueClient.deleteTable(deleteTableRequest);

  }

  private Collection<Column> transformSchema(JsonNode jsonSchema) {
    if (jsonSchema.has("properties")) {
      Map<String, JsonNode> properties = objectMapper.convertValue(jsonSchema.get("properties"), new TypeReference<>() {});
      return properties.entrySet().stream()
          .map(es -> new Column().withName(es.getKey()).withType(transformSchemaRecursive(es.getValue())))
          .collect(Collectors.toSet());
    } else {
      return Collections.emptySet();
    }
  }

  private String transformSchemaRecursive(JsonNode jsonNode) {
    String type = filterTypes(jsonNode.get("type")).iterator().next();
    return switch (type) {
      // TODO(itaseski) support date-time and timestamp airbyte types
      case "string" -> "string";
      case "number" -> {
        if (jsonNode.has("airbyte_type") && jsonNode.get("airbyte_type").asText().equals("integer")) {
          yield "int";
        }
        // Default to use decimal as it is a more precise type and allows for large values
        // Set the default scale and precision to 38 to allow or the widest range of values
        yield "decimal(38,38)";
      }
      case "boolean" -> "boolean";
      case "integer" -> "int";
      case "array" -> {
        String arrayType = "array<";
        Set<String> itemTypes;
        if (jsonNode.has("items")) {
          itemTypes = filterTypes(jsonNode.get("items").get("type"));
        if (itemTypes.size() > 1) {
          // TODO(itaseski) use union instead of array when having multiple types (rare occurrence)?
          arrayType += "string>";
        } else {
          String subtype = transformSchemaRecursive(jsonNode.get("items"));
          arrayType += (subtype + ">");
        }
        } else arrayType += "string>";
        yield arrayType;
      }
      case "object" -> {
        if (jsonNode.has("properties")) {
          String objectType = "struct<";
          Map<String, JsonNode> properties = objectMapper.convertValue(jsonNode.get("properties"), new TypeReference<>() {});
          String columnTypes = properties.entrySet().stream()
              .map(p -> p.getKey() + ":" + transformSchemaRecursive(p.getValue()))
              .collect(Collectors.joining(","));
          objectType += (columnTypes + ">");
          yield objectType;
        } else {
          yield "string";
        }
      }
      default -> type;
    };
  }

  private Set<String> filterTypes(JsonNode type) {
    if (type.isArray()) {
      Set<String> types = objectMapper.convertValue(type, new TypeReference<>() {});
      return types.stream().filter(t -> !t.equals("null")).collect(Collectors.toSet());
    } else {
      return Set.of(type.asText());
    }
  }

  @Override
  public void close() {
    awsGlueClient.shutdown();
  }

}
