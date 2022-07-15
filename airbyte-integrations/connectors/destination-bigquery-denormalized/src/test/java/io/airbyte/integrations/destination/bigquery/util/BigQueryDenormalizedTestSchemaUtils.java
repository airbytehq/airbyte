/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class BigQueryDenormalizedTestSchemaUtils {

  private static final String JSON_FILES_BASE_LOCATION = "schemas/";

  public static JsonNode getSchema() {
    return getTestDataFromResourceJson("schema.json");
  }

  public static JsonNode getSchemaWithFormats() {
    return getTestDataFromResourceJson("schemaWithFormats.json");
  }

  public static JsonNode getSchemaWithDateTime() {
    return getTestDataFromResourceJson("schemaWithDateTime.json");
  }

  public static JsonNode getSchemaWithBigInteger() {
    return getTestDataFromResourceJson("schemaWithBigInteger.json");
  }

  public static JsonNode getSchemaWithInvalidArrayType() {
    return getTestDataFromResourceJson("schemaWithInvalidArrayType.json");
  }

  public static JsonNode getSchemaWithReferenceDefinition() {
    return getTestDataFromResourceJson("schemaWithReferenceDefinition.json");
  }

  public static JsonNode getSchemaWithNestedDatetimeInsideNullObject() {
    return getTestDataFromResourceJson("schemaWithNestedDatetimeInsideNullObject.json");
  }

  public static JsonNode getExpectedSchema() {
    return getTestDataFromResourceJson("expectedSchema.json");
  }

  public static JsonNode getExpectedSchemaWithFormats() {
    return getTestDataFromResourceJson("expectedSchemaWithFormats.json");
  }

  public static JsonNode getExpectedSchemaWithDateTime() {
    return getTestDataFromResourceJson("expectedSchemaWithDateTime.json");
  }

  public static JsonNode getExpectedSchemaWithInvalidArrayType() {
    return getTestDataFromResourceJson("expectedSchemaWithInvalidArrayType.json");
  }

  public static JsonNode getExpectedSchemaWithReferenceDefinition() {
    return getTestDataFromResourceJson("expectedSchemaWithReferenceDefinition.json");
  }

  public static JsonNode getExpectedSchemaWithNestedDatetimeInsideNullObject() {
    return getTestDataFromResourceJson("expectedSchemaWithNestedDatetimeInsideNullObject.json");
  }

  private static JsonNode getTestDataFromResourceJson(final String fileName) {
    final String fileContent;
    try {
      fileContent = Files.readString(Path.of(BigQueryDenormalizedTestSchemaUtils.class.getClassLoader()
          .getResource(JSON_FILES_BASE_LOCATION + fileName).getPath()));
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    return Jsons.deserialize(fileContent);
  }

}
