/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.azure_blob_storage.csv;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.integrations.destination.azure_blob_storage.csv.AzureBlobStorageCsvFormatConfig.Flattening;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("AzureBlobStorageCsvFormatConfig")
public class AzureBlobStorageCsvFormatConfigTest {

  @Test
  @DisplayName("Flattening enums can be created from value string")
  public void testFlatteningCreationFromString() {
    assertEquals(Flattening.NO, Flattening.fromValue("no flattening"));
    assertEquals(Flattening.ROOT_LEVEL, Flattening.fromValue("root level flattening"));
    try {
      Flattening.fromValue("invalid flattening value");
    } catch (final Exception e) {
      assertTrue(e instanceof IllegalArgumentException);
    }
  }

}
