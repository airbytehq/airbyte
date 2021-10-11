/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig;
import io.airbyte.integrations.destination.s3.csv.S3CsvFormatConfig.Flattening;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("S3FormatConfigs")
public class S3FormatConfigsTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("When CSV format is specified, it returns CSV format config")
  public void testGetCsvS3FormatConfig() {
    ObjectNode stubFormatConfig = mapper.createObjectNode();
    stubFormatConfig.put("format_type", S3Format.CSV.toString());
    stubFormatConfig.put("flattening", Flattening.ROOT_LEVEL.getValue());

    ObjectNode stubConfig = mapper.createObjectNode();
    stubConfig.set("format", stubFormatConfig);
    S3FormatConfig formatConfig = S3FormatConfigs.getS3FormatConfig(stubConfig);
    assertEquals(formatConfig.getFormat(), S3Format.CSV);
    assertTrue(formatConfig instanceof S3CsvFormatConfig);
    S3CsvFormatConfig csvFormatConfig = (S3CsvFormatConfig) formatConfig;
    assertEquals(csvFormatConfig.getFlattening(), Flattening.ROOT_LEVEL);
  }

}
