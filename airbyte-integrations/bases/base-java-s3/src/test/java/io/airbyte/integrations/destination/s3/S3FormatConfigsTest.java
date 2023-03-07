/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import io.airbyte.integrations.destination.s3.util.CompressionType;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("S3FormatConfigs")
public class S3FormatConfigsTest {

  @Test
  @DisplayName("When CSV format is specified, it returns CSV format config")
  public void testGetCsvS3FormatConfig() {
    final JsonNode configJson = Jsons.jsonNode(Map.of(
        "format", Jsons.jsonNode(Map.of(
            "format_type", S3Format.CSV.toString(),
            "flattening", Flattening.ROOT_LEVEL.getValue(),
            "compression", Jsons.jsonNode(Map.of(
                "compression_type", "No Compression"))))));

    final S3FormatConfig formatConfig = S3FormatConfigs.getS3FormatConfig(configJson);
    assertEquals(formatConfig.getFormat(), S3Format.CSV);
    assertTrue(formatConfig instanceof S3CsvFormatConfig);
    final S3CsvFormatConfig csvFormatConfig = (S3CsvFormatConfig) formatConfig;
    assertEquals(Flattening.ROOT_LEVEL, csvFormatConfig.getFlattening());
    assertEquals(CompressionType.NO_COMPRESSION, csvFormatConfig.getCompressionType());
  }

}
