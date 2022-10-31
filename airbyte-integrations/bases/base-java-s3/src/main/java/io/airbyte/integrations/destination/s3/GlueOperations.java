package io.airbyte.integrations.destination.s3;

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
import java.io.IOException;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.UnaryOperator;
import java.util.stream.Collectors;

//TODO (itaseski) implement wrapper for retry logic on transient errors
public class GlueOperations implements MetastoreOperations {

    private final ObjectMapper objectMapper;

    private final AWSGlue awsGlueClient;

    public GlueOperations(AWSGlue awsGlueClient) {
        Preconditions.checkArgument(awsGlueClient != null);
        this.awsGlueClient = awsGlueClient;
        this.objectMapper = new ObjectMapper();
    }

    //TODO (itaseski) can location change after table is created?
    @Override
    public void upsertTable(String databaseName, String tableName, String location, JsonNode jsonSchema) {
        try {
            GetTableRequest getTableRequest = new GetTableRequest()
                .withDatabaseName(databaseName)
                .withName(tableName);

            // Will throw EntityNotFoundException if table doesn't exist
            awsGlueClient.getTable(getTableRequest);

            UpdateTableRequest updateTableRequest = new UpdateTableRequest()
                .withDatabaseName(databaseName)
                //TODO (itaseski) do we need to send all table inputs or the ones that are going to be changed?
                .withTableInput(
                    new TableInput()
                        .withName(tableName)
                        .withStorageDescriptor(
                            new StorageDescriptor()
                                .withLocation(location)
                                .withColumns(transformSchema(jsonSchema))
                        )
                );

            awsGlueClient.updateTable(updateTableRequest);
        } catch (EntityNotFoundException enfe) {
            CreateTableRequest createTableRequest = new CreateTableRequest()
                .withDatabaseName(databaseName)
                .withTableInput(
                    new TableInput()
                        .withName(tableName)
                        .withTableType("GOVERNED")
                        .withStorageDescriptor(
                            new StorageDescriptor()
                                .withLocation(location)
                                .withColumns(transformSchema(jsonSchema))
                                .withInputFormat("org.apache.hadoop.mapred.TextInputFormat")
                                .withOutputFormat("org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat")
                                .withSerdeInfo(
                                    new SerDeInfo()
                                        .withSerializationLibrary("org.openx.data.jsonserde.JsonSerDe")
                                        .withParameters(Map.of("paths", ","))
                                )
                        )
                        .withPartitionKeys(List.of())
                        .withParameters(Map.of("classification", "json"))
                );

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

    public Collection<Column> transformSchema(JsonNode jsonSchema) {

        UnaryOperator<String> typeMapper = type -> switch (type) {
            case "string" -> "string";
            case "number" -> "float";
            // TODO (itaseski) does the airbyte schema support integers as first class types or as airbyte_types?
            case "integer" -> "int";
            case "boolean" -> "boolean";
            // TODO (itaseski) throw exception on unknown types or set as received?
            default -> type;
        };

        Map<String, JsonNode> properties = objectMapper.convertValue(jsonSchema.get("properties"), new TypeReference<>() {});

        return properties.entrySet().stream()
            .map(es -> {
                String type = filterTypes(es.getValue().get("type")).iterator().next();
                return switch (type) {
                    case "array" -> {
                        Set<String> types = filterTypes(es.getValue().get("items").get("type"));
                        if (types.size() > 1) {
                            yield new Column().withName(es.getKey()).withType("array<string>");
                        } else {
                            yield new Column().withName(es.getKey())
                                .withType("array<" + typeMapper.apply(types.iterator().next()) + ">");
                        }
                    }
                    case "object" -> {
                        //TODO (itaseski) should we take into account nested objects and generate nested structs i.e struct<col_name : struct<col_name : string>>
                        Map<String, JsonNode> objProperties = objectMapper.convertValue(es.getValue().get("properties"), new TypeReference<>() {});
                        String columns = objProperties.entrySet().stream()
                            .map(ens -> ens.getKey() + " : " + typeMapper.apply(filterTypes(ens.getValue().get("type")).iterator().next()))
                            .collect(Collectors.joining(","));

                        yield new Column().withName(es.getKey()).withType("struct<" + columns  + ">");
                    }
                    default -> new Column().withName(es.getKey()).withType(typeMapper.apply(type));
                };
            })
            .toList();
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
    public void close() throws IOException {
        awsGlueClient.shutdown();
    }
}
