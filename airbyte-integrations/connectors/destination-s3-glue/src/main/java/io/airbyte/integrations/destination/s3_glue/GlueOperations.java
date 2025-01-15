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
import java.util.ArrayList;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.cdk.integrations.destination.s3.S3DestinationConfig;
import io.airbyte.cdk.integrations.destination.s3.S3Format;
import io.airbyte.cdk.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.protocol.models.v0.SyncMode;

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
                          String serializationLibrary,
                          S3DestinationConfig s3DestinationConfig,
                          SyncMode syncMode) {
    try {
      GetTableRequest getTableRequest = new GetTableRequest()
          .withDatabaseName(databaseName)
          .withName(tableName);

      // Will throw EntityNotFoundException if table doesn't exist
      awsGlueClient.getTable(getTableRequest);

      UpdateTableRequest updateTableRequest = new UpdateTableRequest()
          .withDatabaseName(databaseName)
          .withTableInput(this.tableInputBuilder(tableName, s3DestinationConfig.getFormatConfig().getFormat(), location, jsonSchema, serializationLibrary, syncMode));

      awsGlueClient.updateTable(updateTableRequest);
    } catch (EntityNotFoundException enfe) {
      CreateTableRequest createTableRequest = new CreateTableRequest()
          .withDatabaseName(databaseName)
          .withTableInput(this.tableInputBuilder(tableName, s3DestinationConfig.getFormatConfig().getFormat(), location, jsonSchema, serializationLibrary, syncMode));

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

private Collection<Column> transformSchema(JsonNode jsonSchema, S3Format s3Format) {
  if (jsonSchema.has("properties")) {
    Map<String, JsonNode> properties = objectMapper.convertValue(jsonSchema.get("properties"), new TypeReference<>() {});
    return properties.entrySet().stream()
        .map(es -> {
          String key = AvroConstants.NAME_TRANSFORMER.getIdentifier(es.getKey());
          return new Column().withName(key).withType(transformSchemaRecursive(es.getValue(), s3Format));
        })
        .collect(Collectors.toSet());
  } else {
    return Collections.emptySet();
  }
}

  private String transformSchemaRecursive(JsonNode jsonNode, S3Format s3Format) {
    String type = filterTypes(jsonNode.get("type")).iterator().next();
    return switch (type) {
      case "string" -> {
        if (jsonNode.has("format") && jsonNode.get("format").asText().equals("date-time")) {
          yield "struct<member0:timestamp,member1:string>";
        }
        if (jsonNode.has("format") && jsonNode.get("format").asText().equals("date")) {
          yield "struct<member0:date,member1:string>";
        }
        yield "string";
      }
      case "number" -> {
        if (jsonNode.has("airbyte_type") && jsonNode.get("airbyte_type").asText().equals("integer")) {
          yield switch (s3Format) {
            case JSONL -> "integer";
            case PARQUET -> "bigint"; // bigint required here for Parquet + Glue + Redshift queryability
            default -> throw new RuntimeException("Unexpected output format: " + s3Format);
          };
        }
       yield switch (s3Format) { 
          // Default to use decimal as it is a more precise type and allows for large values
          // Set the default scale 38 to allow for the widest range of values
          case JSONL -> "decimal(38)";
          // Avro conversion uses doubles:
          case PARQUET -> "double"; 
          default -> throw new RuntimeException("Unexpected output format: " + s3Format);
        };
      }
      case "boolean" -> "boolean";
      case "integer" -> {yield switch (s3Format) { 
          // Default to use decimal as it is a more precise type and allows for large values
          // Set the default scale 38 to allow for the widest range of values
          case JSONL -> "decimal(38)";
          // Avro conversion uses doubles:
          case PARQUET -> "bigint"; // bigint required here for Parquet + Glue + Redshift queryability
          default -> throw new RuntimeException("Unexpected output format: " + s3Format);
        };
      }
      case "array" -> {
        String arrayType = "array<";
        Set<String> itemTypes;
        if (jsonNode.has("items")) {
          itemTypes = filterTypes(jsonNode.get("items").get("type"));
          if (itemTypes.size() > 1) {
            // TODO(itaseski) use union instead of array when having multiple types (rare occurrence)?
            arrayType += "string>";
          } else {
            String subtype = transformSchemaRecursive(jsonNode.get("items"), s3Format);
            arrayType += (subtype + ">");
          }
        } else
          arrayType += "string>";
        yield arrayType;
      }
      case "object" -> {
        if (jsonNode.has("properties")) {
          String objectType = "struct<";
          Map<String, JsonNode> properties = objectMapper.convertValue(jsonNode.get("properties"), new TypeReference<>() {});
          Stream<String> columnTypesStream = properties.entrySet().stream()
              .map(p -> p.getKey() + ":" + transformSchemaRecursive(p.getValue(), s3Format));
          String columnTypes = Stream.concat(columnTypesStream, Stream.of("_airbyte_additional_properties:map<string,string>"))
              .collect(Collectors.joining(","));
          objectType += (columnTypes + ">");
          yield objectType;
        } else {
          yield switch (s3Format) {
            case JSONL -> "string";
            // Avro conversion uses doubles:
            case PARQUET -> "binary";
            default -> throw new RuntimeException("Unexpected output format: " + s3Format);
          };
        }
      }
      case "null" -> "binary";
      default -> type;
    };
  }

  private Set<String> filterTypes(JsonNode type) {
    // An unknown or null type isn't really going to be readable here by downstream systems (e.g. Redshift).
    // Set this to be binary as the 'safest' choice to allow consumers to best determine how to read it
    if (type == null || type.equals("unknown") || type.equals("null")) {
      return Set.of("binary");
    }
    // Union Type
    if (type.isArray()) {
      Set<String> types = objectMapper.convertValue(type, new TypeReference<>() {});
      Set<String> collectedTypes = types.stream().filter(t -> !t.equals("null")).collect(Collectors.toSet());
      if (collectedTypes.size() > 1) {
        // Union Type, treat as binary
        return Set.of("binary");
      } else {
        return collectedTypes;
      }
    } else {
      return Set.of(type.asText());
    }
  }

  @Override
  public void close() {
    awsGlueClient.shutdown();
  }

  private TableInput tableInputBuilder(String tableName, S3Format s3Format, String location, JsonNode jsonSchema, String serializationLibrary, SyncMode syncMode) {
    ArrayList<Column> columns = new ArrayList<>(transformSchema(jsonSchema, s3Format));
    columns.add(new Column().withName(JavaBaseConstants.COLUMN_NAME_AB_ID).withType("string"));
    columns.add(new Column().withName(JavaBaseConstants.COLUMN_NAME_EMITTED_AT).withType("timestamp"));
    columns.add(new Column().withName("_airbyte_additional_properties").withType("map<string,string>"));

    StorageDescriptor baseDescriptor = new StorageDescriptor()
      .withLocation(location)
      .withColumns(columns);

    baseDescriptor = switch (s3Format) {
      case PARQUET ->
        baseDescriptor
          .withInputFormat("org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat")
          .withOutputFormat("org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat")
          .withSerdeInfo(
            new SerDeInfo()
              .withSerializationLibrary("org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe")
              .withParameters(Map.of("serialization.format", "1")));
      case JSONL ->
        baseDescriptor
          .withInputFormat("org.apache.hadoop.mapred.TextInputFormat")
          .withOutputFormat("org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat")
          .withSerdeInfo(
            new SerDeInfo()
              .withSerializationLibrary(serializationLibrary)
              .withParameters(Map.of("paths", ",")));
      default ->
        throw new RuntimeException("Unexpected output format: " + s3Format);
    };

    Map<String, String> parameters = Map.of(
      "classification", s3Format.toString().toLowerCase(),
       "typeOfData", "file",
       "syncMode", syncMode.toString()
       );

    return new TableInput()
      .withName(tableName)
      .withTableType("EXTERNAL_TABLE")
      .withStorageDescriptor(baseDescriptor)
      .withPartitionKeys(List.of())
      .withParameters(parameters);
  }
}