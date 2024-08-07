/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.starburst_galaxy;

import static io.airbyte.commons.json.Jsons.deserialize;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyS3StreamCopier.convertIcebergSchemaToGalaxySchema;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyS3StreamCopier.getAvroSchema;
import static io.airbyte.integrations.destination.starburst_galaxy.StarburstGalaxyS3StreamCopier.getIcebergSchema;
import static java.util.Objects.requireNonNull;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.slf4j.LoggerFactory.getLogger;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.apache.iceberg.Schema;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;

public class TypeConversionTest {

  private static final Logger LOGGER = getLogger(TypeConversionTest.class);
  private static final String INPUT_FILES_BASE_LOCATION = "schemas/";

  @Test
  public void testJsonV0SchemaTypesConversion() {
    runTests(getTestDataFromResourceJson("type_conversion_test_cases_v0.json"));
  }

  @Test
  public void testJsonV1SchemaTypesConversion() {
    runTests(getTestDataFromResourceJson("type_conversion_test_cases_v1.json"));
  }

  private void runTests(JsonNode testCases) {
    for (JsonNode testCase : testCases) {
      String schemaName = testCase.get("schemaName").asText();
      JsonNode galaxyIcebergSchema = testCase.get("galaxyIcebergSchema");
      JsonNode jsonSchema = testCase.get("jsonSchema");
      LOGGER.info("Executing {} test", schemaName);
      compareSchemas(jsonSchema, galaxyIcebergSchema);
    }
  }

  private static JsonNode getTestDataFromResourceJson(String fileName) {
    try {
      String fileContent = Files.readString(Path.of(requireNonNull(TypeConversionTest.class.getClassLoader()
          .getResource(INPUT_FILES_BASE_LOCATION + fileName)).getPath()));
      return deserialize(fileContent);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  private void compareSchemas(JsonNode jsonSchema, JsonNode expectedIcebergGalaxySchema) {
    Schema icebergSchema = getIcebergSchema(getAvroSchema("stream", "namespace", jsonSchema));
    TableSchema galaxySchema = convertIcebergSchemaToGalaxySchema(icebergSchema);
    assertEquals(galaxySchema.columns().size(), expectedIcebergGalaxySchema.size());
    for (ColumnMetadata columnMetadata : galaxySchema.columns()) {
      JsonNode expectedIcebergType = expectedIcebergGalaxySchema.get(columnMetadata.name());
      assertEquals(expectedIcebergType.textValue(), columnMetadata.galaxyIcebergType().getDisplayName());
    }
  }

}
