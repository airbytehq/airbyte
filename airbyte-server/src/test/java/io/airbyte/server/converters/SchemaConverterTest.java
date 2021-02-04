/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DataType;
import io.airbyte.server.helpers.ConnectionHelpers;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class SchemaConverterTest {

  @Test
  void convertToProtocol() {
    assertEquals(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog(), SchemaConverter.convertTo(ConnectionHelpers.generateBasicApiCatalog()));
  }

  @Test
  void convertToAPI() {
    assertEquals(ConnectionHelpers.generateBasicApiCatalog(), SchemaConverter.convertTo(ConnectionHelpers.generateBasicConfiguredAirbyteCatalog()));
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(io.airbyte.api.model.DataType.class, DataType.class));
    assertTrue(Enums.isCompatible(io.airbyte.config.SyncMode.class, io.airbyte.api.model.SyncMode.class));
  }

  @Test
  void testExtractProperties() throws IOException {
    final JsonNode schema = getTestNestedPropertiesJson();
    final Map<List<String>, JsonNode> properties = SchemaConverter.extractProperties(schema);
    final List<String> actual = new ArrayList<>();
    properties.forEach((k, v) -> actual.add(k.get(0)));

    final List<String> expected = List.of(
        "vid",
        "items",
        "profile-url",
        "timestamp",
        "source",
        "is-contact",
        "value",
        "profile-token");

    assertEquals(expected, actual);
  }

  public static JsonNode getTestNestedPropertiesJson() throws IOException {
    final Path path =
        Paths.get("../airbyte-server/src/test/resources/json/TestNestedProperties.json");
    return Jsons.deserialize(Files.readString(path));
  }

}
