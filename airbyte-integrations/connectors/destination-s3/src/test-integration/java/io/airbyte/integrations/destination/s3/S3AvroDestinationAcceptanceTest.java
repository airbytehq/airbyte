/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectReader;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.destination.s3.avro.AvroConstants;
import io.airbyte.integrations.destination.s3.avro.JsonFieldNameUpdater;
import io.airbyte.integrations.destination.s3.avro.JsonSchemaType;
import io.airbyte.integrations.destination.s3.util.AvroRecordHelper;
import io.airbyte.integrations.standardtest.destination.comparator.TestDataComparator;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;
import org.apache.avro.Schema;
import org.apache.avro.Schema.Type;
import org.apache.avro.file.DataFileReader;
import org.apache.avro.file.SeekableByteArrayInput;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericData.Record;
import org.apache.avro.generic.GenericDatumReader;
import org.junit.jupiter.api.Test;

public class S3AvroDestinationAcceptanceTest extends S3DestinationAcceptanceTest {

  protected S3AvroDestinationAcceptanceTest() {
    super(S3Format.AVRO);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.jsonNode(Map.of(
        "format_type", "Avro",
        "compression_codec", Map.of(
            "codec", "zstandard",
            "compression_level", 5,
            "include_checksum", true)));
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws Exception {
    final JsonFieldNameUpdater nameUpdater = AvroRecordHelper.getFieldNameUpdater(streamName, namespace, streamSchema);

    final List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);
    final List<JsonNode> jsonRecords = new LinkedList<>();

    for (final S3ObjectSummary objectSummary : objectSummaries) {
      final S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      try (final DataFileReader<Record> dataFileReader = new DataFileReader<>(
          new SeekableByteArrayInput(object.getObjectContent().readAllBytes()),
          new GenericDatumReader<>())) {
        final ObjectReader jsonReader = MAPPER.reader();
        while (dataFileReader.hasNext()) {
          final GenericData.Record record = dataFileReader.next();
          final byte[] jsonBytes = AvroConstants.JSON_CONVERTER.convertToJson(record);
          JsonNode jsonRecord = jsonReader.readTree(jsonBytes);
          jsonRecord = nameUpdater.getJsonWithOriginalFieldNames(jsonRecord);
          jsonRecords.add(AvroRecordHelper.pruneAirbyteJson(jsonRecord));
        }
      }
    }

    return jsonRecords;
  }

  @Override
  protected TestDataComparator getTestDataComparator() {
    return new S3AvroParquetTestDataComparator();
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

      Set<Type> actualSchemaTypes = retrieveDataTypesFromSchema(streamName, schema);
      Optional<Type> actualSchemaTypesWithoutNull = actualSchemaTypes.stream().filter(type -> !type.equals(Type.NULL)).findAny();

      List<Type> expectedTypeList = createSchemaTypesForStreamName(stream.getJsonSchema().get("properties").get("data"));
      assertEquals(1, expectedTypeList.size(), "Several non null data types are not supported for single stream");
      assertTrue(actualSchemaTypesWithoutNull.isPresent());
      assertEquals(expectedTypeList.get(0), actualSchemaTypesWithoutNull.get());
    }
  }

  private List<Type> createSchemaTypesForStreamName(JsonNode fieldDefinition) {
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

  private Set<Type> retrieveDataTypesFromSchema(final String streamName, final String namespace) throws Exception {

    final List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);
    Set<Type> dataTypes = new HashSet<>();

    for (final S3ObjectSummary objectSummary : objectSummaries) {
      final S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
      try (final DataFileReader<Record> dataFileReader = new DataFileReader<>(
          new SeekableByteArrayInput(object.getObjectContent().readAllBytes()),
          new GenericDatumReader<>())) {
        while (dataFileReader.hasNext()) {
          final GenericData.Record record = dataFileReader.next();
          record.getSchema().getField("data").schema();
          List<Schema> listAvroTypes = record
              .getSchema()
              .getField("data")
              .schema()
              .getTypes();

          Set<Type> actualDataTypes = listAvroTypes
              .stream()
              .map(Schema::getType)
              .collect(Collectors.toSet());
          dataTypes.addAll(actualDataTypes);
        }
      }
    }

    return dataTypes;
  }

}
