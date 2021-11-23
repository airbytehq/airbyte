/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.enums.Enums;
import io.airbyte.config.DataType;
import io.airbyte.server.helpers.ConnectionHelpers;
import org.junit.jupiter.api.Test;

class CatalogConverterTest {

  @Test
  void testConvertToProtocol() {
    assertEquals(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog(), CatalogConverter.toProtocol(ConnectionHelpers.generateBasicApiCatalog()));
  }

  @Test
  void testConvertToAPI() {
    assertEquals(ConnectionHelpers.generateBasicApiCatalog(), CatalogConverter.toApi(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog()));
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(io.airbyte.api.model.DataType.class, DataType.class));
    assertTrue(Enums.isCompatible(io.airbyte.config.SyncMode.class, io.airbyte.api.model.SyncMode.class));
  }

}
