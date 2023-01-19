/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.JsonSchemaType;
import io.airbyte.integrations.standardtest.destination.ProtocolVersion;
import io.airbyte.integrations.standardtest.destination.argproviders.NumberDataTypeTestArgumentProvider;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;
import org.apache.avro.Schema;
import org.apache.avro.Schema.Field;
import org.apache.avro.Schema.Type;
import org.apache.avro.generic.GenericData.Record;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

public abstract class GcsAvroParquetDestinationAcceptanceTest extends GcsDestinationAcceptanceTest {

  public GcsAvroParquetDestinationAcceptanceTest(final S3Format s3Format) {
    super(s3Format);
  }

  @Override
  public ProtocolVersion getProtocolVersion() {
    return ProtocolVersion.V1;
  }

  @ParameterizedTest
  @ArgumentsSource(NumberDataTypeTestArgumentProvider.class)
  public void testNumberDataType(final String catalogFileName, final String messagesFileName) throws Exception {
    final AirbyteCatalog catalog = readCatalogFromFile(catalogFileName);
    final List<AirbyteMessage> messages = readMessagesFromFile(messagesFileName);

    final JsonNode config = getConfig();
    final String defaultSchema = getDefaultSchema(config);
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);

    for (final AirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getName();
      final String schema = stream.getNamespace() != null ? stream.getNamespace() : defaultSchema;

      final Map<String, Set<Type>> actualSchemaTypes = retrieveDataTypesFromPersistedFiles(streamName, schema);
      final Map<String, Set<Type>> expectedSchemaTypes = retrieveExpectedDataTypes(stream);

      assertEquals(expectedSchemaTypes, actualSchemaTypes);
    }
  }

  private Map<String, Set<Type>> retrieveExpectedDataTypes(final AirbyteStream stream) {
    final Iterable<String> iterableNames = () -> stream.getJsonSchema().get("properties").fieldNames();
    final Map<String, JsonNode> nameToNode = StreamSupport.stream(iterableNames.spliterator(), false)
        .collect(Collectors.toMap(
            Function.identity(),
            name -> getJsonNode(stream, name)));

    return nameToNode
        .entrySet()
        .stream()
        .collect(Collectors.toMap(
            Entry::getKey,
            entry -> getExpectedSchemaType(entry.getValue())));
  }

  private JsonNode getJsonNode(final AirbyteStream stream, final String name) {
    final JsonNode properties = stream.getJsonSchema().get("properties");
    if (properties.size() == 1) {
      return properties.get("data");
    }
    return properties.get(name).get("items");
  }

  private Set<Type> getExpectedSchemaType(final JsonNode fieldDefinition) {
    // The $ref is a migration to V1 data type protocol see well_known_types.yaml
    final JsonNode typeProperty = fieldDefinition.get("type") == null ? fieldDefinition.get("$ref") : fieldDefinition.get("type");
    final JsonNode airbyteTypeProperty = fieldDefinition.get("airbyte_type");
    final String airbyteTypePropertyText = airbyteTypeProperty == null ? null : airbyteTypeProperty.asText();
    return Arrays.stream(JsonSchemaType.values())
        .filter(
            value -> value.getJsonSchemaType().equals(typeProperty.asText()) && compareAirbyteTypes(airbyteTypePropertyText, value))
        .map(JsonSchemaType::getAvroType)
        .collect(Collectors.toSet());
  }

  private boolean compareAirbyteTypes(final String airbyteTypePropertyText, final JsonSchemaType value) {
    if (airbyteTypePropertyText == null) {
      return value.getJsonSchemaAirbyteType() == null;
    }
    return airbyteTypePropertyText.equals(value.getJsonSchemaAirbyteType());
  }

  private AirbyteCatalog readCatalogFromFile(final String catalogFilename) throws IOException {
    return Jsons.deserialize(MoreResources.readResource(catalogFilename), AirbyteCatalog.class);
  }

  private List<AirbyteMessage> readMessagesFromFile(final String messagesFilename) throws IOException {
    return MoreResources.readResource(messagesFilename).lines()
        .map(record -> Jsons.deserialize(record, AirbyteMessage.class)).collect(Collectors.toList());
  }

  protected abstract Map<String, Set<Type>> retrieveDataTypesFromPersistedFiles(final String streamName, final String namespace) throws Exception;

  protected Map<String, Set<Type>> getTypes(final Record record) {

    final List<Field> fieldList = record
        .getSchema()
        .getFields()
        .stream()
        .filter(field -> !field.name().startsWith("_airbyte"))
        .toList();

    if (fieldList.size() == 1) {
      return fieldList
          .stream()
          .collect(
              Collectors.toMap(
                  Field::name,
                  field -> field.schema().getTypes().stream().map(Schema::getType).filter(type -> !type.equals(Type.NULL))
                      .collect(Collectors.toSet())));
    } else {
      return fieldList
          .stream()
          .collect(
              Collectors.toMap(
                  Field::name,
                  field -> field.schema().getTypes()
                      .stream().filter(type -> !type.getType().equals(Type.NULL))
                      .flatMap(type -> type.getElementType().getTypes().stream()).map(Schema::getType).filter(type -> !type.equals(Type.NULL))
                      .collect(Collectors.toSet())));
    }
  }

}
