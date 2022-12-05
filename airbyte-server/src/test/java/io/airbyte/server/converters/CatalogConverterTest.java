/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.api.model.generated.AirbyteCatalog;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.DataType;
import io.airbyte.server.handlers.helpers.CatalogConverter;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.validation.json.JsonValidationException;
import org.junit.jupiter.api.Test;

class CatalogConverterTest {

  @Test
  void testConvertToProtocol() throws JsonValidationException {
    assertEquals(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog(), CatalogConverter.toProtocol(ConnectionHelpers.generateBasicApiCatalog()));
  }

  @Test
  void testConvertToAPI() {
    final AirbyteCatalog expectedCatalog = ConnectionHelpers.generateBasicApiCatalog();
    assertEquals(ConnectionHelpers.generateBasicApiCatalog(), CatalogConverter.toApi(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog(),
        CatalogConverter.getFieldSelectionEnabledStreams(expectedCatalog)));
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(io.airbyte.api.model.generated.DataType.class, DataType.class));
    assertTrue(Enums.isCompatible(io.airbyte.config.SyncMode.class, io.airbyte.api.model.generated.SyncMode.class));
  }

}
