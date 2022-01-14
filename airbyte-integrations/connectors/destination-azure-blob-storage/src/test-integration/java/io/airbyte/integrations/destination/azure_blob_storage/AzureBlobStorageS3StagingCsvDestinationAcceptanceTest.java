/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.StreamSupport;
import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVRecord;
import org.apache.commons.csv.QuoteMode;

public class AzureBlobStorageS3StagingCsvDestinationAcceptanceTest extends
    AzureBlobStorageS3StagingDestinationAcceptanceTest {

  protected static final ObjectMapper MAPPER = MoreMappers.initMapper();

  public AzureBlobStorageS3StagingCsvDestinationAcceptanceTest() {
    super(AzureBlobStorageFormat.CSV);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.deserialize("{\n"
        + "  \"format_type\": \"CSV\",\n"
        + "  \"flattening\": \"Root level flattening\"\n"
        + "}");
  }

  /**
   * Convert json_schema to a map from field name to field types.
   */
  private static Map<String, String> getFieldTypes(final JsonNode streamSchema) {
    final Map<String, String> fieldTypes = new HashMap<>();
    final JsonNode fieldDefinitions = streamSchema.get("properties");
    final Iterator<Entry<String, JsonNode>> iterator = fieldDefinitions.fields();
    while (iterator.hasNext()) {
      final Entry<String, JsonNode> entry = iterator.next();
      fieldTypes.put(entry.getKey(), entry.getValue().get("type").asText());
    }
    return fieldTypes;
  }

  private static JsonNode getJsonNode(final Map<String, String> input, final Map<String, String> fieldTypes) {
    final ObjectNode json = MAPPER.createObjectNode();

    if (input.containsKey(JavaBaseConstants.COLUMN_NAME_DATA)) {
      return Jsons.deserialize(input.get(JavaBaseConstants.COLUMN_NAME_DATA));
    }

    for (final Entry<String, String> entry : input.entrySet()) {
      final String key = entry.getKey();
      if (key.equals(JavaBaseConstants.COLUMN_NAME_AB_ID) || key
          .equals(JavaBaseConstants.COLUMN_NAME_EMITTED_AT)) {
        continue;
      }
      final String value = entry.getValue();
      if (value == null || value.equals("")) {
        continue;
      }
      final String type = fieldTypes.get(key);
      switch (type) {
        case "boolean" -> json.put(key, Boolean.valueOf(value));
        case "integer" -> json.put(key, Integer.valueOf(value));
        case "number" -> json.put(key, Double.valueOf(value));
        default -> json.put(key, value);
      }
    }
    return json;
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws IOException {
    final String allSyncedObjects = getAllSyncedObjects(streamName);

    final Map<String, String> fieldTypes = getFieldTypes(streamSchema);
    final List<JsonNode> jsonRecords = new LinkedList<>();

    try (final Reader in = new StringReader(allSyncedObjects)) {
      final Iterable<CSVRecord> records = CSVFormat.DEFAULT
          .withQuoteMode(QuoteMode.NON_NUMERIC)
          .withFirstRecordAsHeader()
          .parse(in);

      StreamSupport.stream(records.spliterator(), false)
          .forEach(r -> jsonRecords.add(getJsonNode(r.toMap(), fieldTypes)));
    }

    return jsonRecords;
  }

}
