package io.airbyte.integrations.destination.gcs;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.destination.s3.S3Format;
import io.airbyte.integrations.destination.s3.avro.JsonSchemaType;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.avro.Schema;
import org.apache.avro.Schema.Type;
import org.apache.avro.generic.GenericData.Record;
import org.junit.jupiter.api.Test;

public abstract class GcsAvroParquetDestinationAcceptanceTest extends GcsDestinationAcceptanceTest {

  protected GcsAvroParquetDestinationAcceptanceTest(S3Format s3Format) {
    super(s3Format);
  }

  @Test
  public void testNumberDataType() throws Exception {
    final AirbyteCatalog catalog = readCatalogFromFile("number_data_type_test_catalog.json");
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers.toDefaultConfiguredCatalog(catalog);
    final List<AirbyteMessage> messages = readMessagesFromFile("number_data_type_test_messages.txt");

    final JsonNode config = getConfig();
    final String defaultSchema = getDefaultSchema(config);
    runSyncAndVerifyStateOutput(config, messages, configuredCatalog, false);

    for (final AirbyteStream stream : catalog.getStreams()) {
      final String streamName = stream.getName();
      final String schema = stream.getNamespace() != null ? stream.getNamespace() : defaultSchema;

      Set<Type> actualSchemaTypes = retrieveDataTypesFromPersistedFiles(streamName, schema);
      Optional<Type> actualSchemaTypesWithoutNull = actualSchemaTypes.stream().filter(type -> !type.equals(Type.NULL)).findAny();

      JsonNode fieldDefinition = stream.getJsonSchema().get("properties").get("data");
      List<Type> expectedTypeList = getExpectedSchemaType(fieldDefinition);
      assertEquals(1, expectedTypeList.size(), "Several not null data types are not supported for single stream");
      assertTrue(actualSchemaTypesWithoutNull.isPresent());
      assertEquals(expectedTypeList.get(0), actualSchemaTypesWithoutNull.get());
    }
  }

  private List<Type> getExpectedSchemaType(JsonNode fieldDefinition) {
    final JsonNode typeProperty = fieldDefinition.get("type");
    final JsonNode airbyteTypeProperty = fieldDefinition.get("airbyte_type");
    final String airbyteTypePropertyText = airbyteTypeProperty == null ? null : airbyteTypeProperty.asText();
    return Arrays.stream(JsonSchemaType.values())
        .filter(
            value -> value.getJsonSchemaType().equals(typeProperty.asText()) && compareAirbyteTypes(airbyteTypePropertyText, value))
        .map(JsonSchemaType::getAvroType)
        .toList();
  }

  private boolean compareAirbyteTypes(String airbyteTypePropertyText, JsonSchemaType value) {
    if (airbyteTypePropertyText == null){
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

  protected abstract Set<Type> retrieveDataTypesFromPersistedFiles(final String streamName, final String namespace) throws Exception;

  protected Set<Type> getTypes(Record record) {
    List<Schema> listAvroTypes = record
        .getSchema()
        .getField("data")
        .schema()
        .getTypes();

    return listAvroTypes
        .stream()
        .map(Schema::getType)
        .collect(Collectors.toSet());
  }
}
