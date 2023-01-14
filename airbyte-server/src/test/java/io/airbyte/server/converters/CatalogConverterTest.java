/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import static io.airbyte.server.helpers.ConnectionHelpers.FIELD_NAME;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.api.model.generated.SelectedFieldInfo;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.DataType;
import io.airbyte.config.FieldSelectionData;
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
    assertEquals(ConnectionHelpers.generateBasicApiCatalog(), CatalogConverter.toApi(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog(),
        new FieldSelectionData()));
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(io.airbyte.api.model.generated.DataType.class, DataType.class));
    assertTrue(Enums.isCompatible(io.airbyte.config.SyncMode.class, io.airbyte.api.model.generated.SyncMode.class));
  }

  @Test
  void testConvertToProtocolColumnSelectionValidation() {
    assertThrows(JsonValidationException.class, () -> {
      // fieldSelectionEnabled=true but selectedFields=null.
      final var catalog = ConnectionHelpers.generateBasicApiCatalog();
      catalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true).selectedFields(null);
      CatalogConverter.toProtocol(catalog);
    });

    assertThrows(JsonValidationException.class, () -> {
      // JSON schema has no `properties` node.
      final var catalog = ConnectionHelpers.generateBasicApiCatalog();
      ((ObjectNode) catalog.getStreams().get(0).getStream().getJsonSchema()).remove("properties");
      catalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true).addSelectedFieldsItem(new SelectedFieldInfo().addFieldPathItem("foo"));
      CatalogConverter.toProtocol(catalog);
    });

    assertThrows(JsonValidationException.class, () -> {
      // SelectedFieldInfo with empty path.
      final var catalog = ConnectionHelpers.generateBasicApiCatalog();
      catalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true).addSelectedFieldsItem(new SelectedFieldInfo());
      CatalogConverter.toProtocol(catalog);
    });

    assertThrows(UnsupportedOperationException.class, () -> {
      // SelectedFieldInfo with nested field path.
      final var catalog = ConnectionHelpers.generateBasicApiCatalog();
      catalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true)
          .addSelectedFieldsItem(new SelectedFieldInfo().addFieldPathItem("foo").addFieldPathItem("bar"));
      CatalogConverter.toProtocol(catalog);
    });

    assertThrows(JsonValidationException.class, () -> {
      // SelectedFieldInfo with empty path.
      final var catalog = ConnectionHelpers.generateBasicApiCatalog();
      catalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true).addSelectedFieldsItem(new SelectedFieldInfo().addFieldPathItem("foo"));
      CatalogConverter.toProtocol(catalog);
    });
  }

  @Test
  void testConvertToProtocolFieldSelection() throws JsonValidationException {
    final var catalog = ConnectionHelpers.generateApiCatalogWithTwoFields();
    catalog.getStreams().get(0).getConfig().fieldSelectionEnabled(true).addSelectedFieldsItem(new SelectedFieldInfo().addFieldPathItem(FIELD_NAME));
    assertEquals(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog(), CatalogConverter.toProtocol(catalog));
  }

}
