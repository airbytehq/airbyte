/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import com.amazonaws.services.s3.model.S3Object;
import com.amazonaws.services.s3.model.S3ObjectSummary;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
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

public abstract class S3BaseCsvDestinationAcceptanceTest extends S3DestinationAcceptanceTest {

  public S3BaseCsvDestinationAcceptanceTest() {
    super(S3Format.CSV);
  }

  @Override
  protected JsonNode getFormatConfig() {
    return Jsons.jsonNode(Map.of(
        "format_type", outputFormat,
        "flattening", Flattening.ROOT_LEVEL.getValue(),
        "compression", Jsons.jsonNode(Map.of("compression_type", "No Compression"))));
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
      JsonNode fieldValue = entry.getValue();
      JsonNode typeValue = fieldValue.get("type") == null ? fieldValue.get("$ref") : fieldValue.get("type");
      fieldTypes.put(entry.getKey(), typeValue.asText());
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
        case "WellKnownTypes.json#/definitions/Boolean" -> json.put(key, Boolean.valueOf(value));
        case "WellKnownTypes.json#/definitions/Integer" -> json.put(key, Integer.valueOf(value));
        case "WellKnownTypes.json#/definitions/Number" -> json.put(key, Double.valueOf(value));
        case "boolean" -> json.put(key, Boolean.valueOf(value));
        case "integer" -> json.put(key, Integer.valueOf(value));
        case "number" -> json.put(key, Double.valueOf(value));
        case "" -> addNoTypeValue(json, key, value);
        default -> json.put(key, value);
      }
    }
    return json;
  }

  private static void addNoTypeValue(final ObjectNode json, final String key, final String value) {
    if (value != null && (value.matches("^\\[.*\\]$")) || value.matches("^\\{.*\\}$")) {
      final var newNode = Jsons.deserialize(value);
      json.set(key, newNode);
    } else {
      json.put(key, value);
    }
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema)
      throws IOException {
    final List<S3ObjectSummary> objectSummaries = getAllSyncedObjects(streamName, namespace);

    final Map<String, String> fieldTypes = getFieldTypes(streamSchema);
    final List<JsonNode> jsonRecords = new LinkedList<>();

    for (final S3ObjectSummary objectSummary : objectSummaries) {
      try (final S3Object object = s3Client.getObject(objectSummary.getBucketName(), objectSummary.getKey());
          final Reader in = getReader(object)) {
        final Iterable<CSVRecord> records = CSVFormat.DEFAULT
            .withQuoteMode(QuoteMode.NON_NUMERIC)
            .withFirstRecordAsHeader()
            .parse(in);
        StreamSupport.stream(records.spliterator(), false)
            .forEach(r -> jsonRecords.add(getJsonNode(r.toMap(), fieldTypes)));
      }
    }

    return jsonRecords;
  }

  protected Reader getReader(final S3Object s3Object) throws IOException {
    return new InputStreamReader(s3Object.getObjectContent(), StandardCharsets.UTF_8);
  }

}
