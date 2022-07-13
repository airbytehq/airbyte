/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.integrations.destination.bigquery.BigQueryDenormalizedDestination;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class BigQueryDenormalizedTestDataUtils {

  private static final String JSON_FILES_BASE_LOCATION = "testdata/";

  public static final String USERS_STREAM_NAME = "users";

  public static JsonNode getSchema() {
    return getTestDataFromResourceJson("schema.json");
  }

  public static JsonNode getAnyOfSchema() {
    return getTestDataFromResourceJson("schemaAnyOfAllOf.json");
  }

  public static JsonNode getSchemaWithFormats() {
    return getTestDataFromResourceJson("schemaWithFormats.json");
  }

  public static JsonNode getSchemaWithDateTime() {
    return getTestDataFromResourceJson("schemaWithDateTime.json");
  }

  public static JsonNode getSchemaWithInvalidArrayType() {
    return getTestDataFromResourceJson("schemaWithInvalidArrayType.json");
  }

  public static JsonNode getSchemaArrays() {
    return getTestDataFromResourceJson("schemaArrays.json");
  }

  public static JsonNode getDataArrays() {
    return getTestDataFromResourceJson("dataArrays.json");
  }

  public static JsonNode getSchemaTooDeepNestedDepth() {
    return getTestDataFromResourceJson("schemaTooDeepNestedDepth.json");
  }

  public static JsonNode getDataTooDeepNestedDepth() {
    return getTestDataFromResourceJson("dataTooDeepNestedDepth.json");
  }

  public static JsonNode getSchemaMaxNestedDepth() {
    return getTestDataFromResourceJson("schemaMaxNestedDepth.json");
  }

  public static JsonNode getDataMaxNestedDepth() {
    return getTestDataFromResourceJson("dataMaxNestedDepth.json");
  }

  public static JsonNode getExpectedDataArrays() {
    return getTestDataFromResourceJson("expectedDataArrays.json");
  }

  public static JsonNode getData() {
    return getTestDataFromResourceJson("data.json");
  }

  public static JsonNode getDataWithFormats() {
    return getTestDataFromResourceJson("dataWithFormats.json");
  }

  public static JsonNode getAnyOfFormats() {
    return getTestDataFromResourceJson("dataAnyOfFormats.json");
  }

  public static JsonNode getAnyOfFormatsWithNull() {
    return getTestDataFromResourceJson("dataAnyOfFormatsWithNull.json");
  }

  public static JsonNode getAnyOfFormatsWithEmptyList() {
    return getTestDataFromResourceJson("dataAnyOfFormatsWithEmptyList.json");
  }

  public static JsonNode getDataWithJSONDateTimeFormats() {
    return getTestDataFromResourceJson("dataWithJSONDateTimeFormats.json");
  }

  public static JsonNode getDataWithJSONWithReference() {
    return getTestDataFromResourceJson("dataWithJSONWithReference.json");
  }

  public static JsonNode getSchemaWithReferenceDefinition() {
    return getTestDataFromResourceJson("schemaWithReferenceDefinition.json");
  }

  public static JsonNode getSchemaWithNestedDatetimeInsideNullObject() {
    return getTestDataFromResourceJson("schemaWithNestedDatetimeInsideNullObject.json");
  }

  public static JsonNode getDataWithEmptyObjectAndArray() {
    return getTestDataFromResourceJson("dataWithEmptyObjectAndArray.json");
  }

  public static JsonNode getDataWithNestedDatetimeInsideNullObject() {
    return getTestDataFromResourceJson("dataWithNestedDatetimeInsideNullObject.json");

  }

  private static JsonNode getTestDataFromResourceJson(final String fileName) {
    final String fileContent;
    try {
      fileContent = Files.readString(Path.of(BigQueryDenormalizedTestDataUtils.class.getClassLoader()
          .getResource(JSON_FILES_BASE_LOCATION + fileName).getPath()));
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    return Jsons.deserialize(fileContent);
  }

  public static ConfiguredAirbyteCatalog getCommonCatalog(final JsonNode schema, final String datasetId) {
    return new ConfiguredAirbyteCatalog().withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
        .withStream(new AirbyteStream().withName(USERS_STREAM_NAME).withNamespace(datasetId).withJsonSchema(schema))
        .withSyncMode(SyncMode.FULL_REFRESH).withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));
  }

  public static void runDestinationWrite(ConfiguredAirbyteCatalog catalog, JsonNode config, AirbyteMessage...messages) throws Exception {
    final BigQueryDestination destination = new BigQueryDenormalizedDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);

    for (AirbyteMessage message : messages) {
      consumer.accept(message);
    }
    consumer.close();
  }

}
