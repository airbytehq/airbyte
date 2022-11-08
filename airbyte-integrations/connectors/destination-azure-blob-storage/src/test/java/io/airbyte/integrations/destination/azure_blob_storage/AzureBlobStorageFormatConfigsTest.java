/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.jackson.MoreMappers;
import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvFormatConfig;
import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvFormatConfig.Flattening;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("AzureBlobStorageFormatConfigs")
public class AzureBlobStorageFormatConfigsTest {

  private static final ObjectMapper mapper = MoreMappers.initMapper();

  @Test
  @DisplayName("When CSV format is specified, it returns CSV format config")
  public void testGetCsvS3FormatConfig() {
    final ObjectNode stubFormatConfig = mapper.createObjectNode();
    stubFormatConfig.put("format_type", AzureBlobStorageFormat.CSV.toString());
    stubFormatConfig.put("flattening", Flattening.ROOT_LEVEL.getValue());

    final ObjectNode stubConfig = mapper.createObjectNode();
    stubConfig.set("format", stubFormatConfig);
    final AzureBlobStorageFormatConfig formatConfig = AzureBlobStorageFormatConfigs
        .getAzureBlobStorageFormatConfig(stubConfig);
    assertEquals(formatConfig.getFormat(), AzureBlobStorageFormat.CSV);
    assertTrue(formatConfig instanceof AzureBlobStorageCsvFormatConfig);
    final AzureBlobStorageCsvFormatConfig csvFormatConfig = (AzureBlobStorageCsvFormatConfig) formatConfig;
    assertEquals(csvFormatConfig.getFlattening(), Flattening.ROOT_LEVEL);
  }

}
