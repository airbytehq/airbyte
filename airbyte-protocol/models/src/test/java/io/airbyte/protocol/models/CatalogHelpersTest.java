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

package io.airbyte.protocol.models;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertIterableEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableSet;
import com.google.common.collect.Multimap;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import org.junit.jupiter.api.Test;

class CatalogHelpersTest {

  @Test
  void testFieldToJsonSchema() {
    final String expected = "{ \"type\": \"object\", \"properties\": { \"name\": { \"type\": \"string\" } } } ";
    final JsonNode actual = CatalogHelpers.fieldsToJsonSchema(Field.of("name", JsonSchemaPrimitive.STRING));

    assertEquals(Jsons.deserialize(expected), actual);
  }

  @Test
  void testGetTopLevelFieldNames() {
    final String json = "{ \"type\": \"object\", \"properties\": { \"name\": { \"type\": \"string\" } } } ";
    final Set<String> actualFieldNames =
        CatalogHelpers.getTopLevelFieldNames(new ConfiguredAirbyteStream().withStream(new AirbyteStream().withJsonSchema(Jsons.deserialize(json))));

    assertEquals(Sets.newHashSet("name"), actualFieldNames);
  }

  @Test
  void testValidIdentifiers() {
    assertTrue(CatalogHelpers.isValidIdentifier("identifier_name"));
    assertTrue(CatalogHelpers.isValidIdentifier("iDenTiFieR_name"));
    assertTrue(CatalogHelpers.isValidIdentifier("__identifier_name"));
    assertTrue(CatalogHelpers.isValidIdentifier("IDENTIFIER_NAME"));
    assertTrue(CatalogHelpers.isValidIdentifier("123identifier_name"));
    assertTrue(CatalogHelpers.isValidIdentifier("i0d0e0n0t0i0f0i0e0r0n0a0m0e"));
    assertTrue(CatalogHelpers.isValidIdentifier("identifiêr"));
    assertTrue(CatalogHelpers.isValidIdentifier("a_unicode_name_文"));
    assertTrue(CatalogHelpers.isValidIdentifier("identifier__name__"));
    assertTrue(CatalogHelpers.isValidIdentifier("identifier-name.weee"));
  }

  @Test
  void testInvalidIdentifiers() {
    assertFalse(CatalogHelpers.isValidIdentifier("\"identifier name"));
    assertFalse(CatalogHelpers.isValidIdentifier("identifier name"));
    assertFalse(CatalogHelpers.isValidIdentifier("identifier%"));
    assertFalse(CatalogHelpers.isValidIdentifier("`identifier`"));
    assertFalse(CatalogHelpers.isValidIdentifier("'identifier'"));
  }

  @Test
  void testGetInvalidStreamNames() {
    final String validStreamName = "Valid_Stream";
    final AirbyteStream validStream = new AirbyteStream();
    validStream.setName(validStreamName);

    final String invalidStreamName = "invalid stream";
    AirbyteStream invalidStream = new AirbyteStream();
    invalidStream.setName(invalidStreamName);

    AirbyteCatalog catalog = new AirbyteCatalog();
    catalog.setStreams(List.of(validStream, invalidStream));

    List<String> invalidStreamNames = CatalogHelpers.getInvalidStreamNames(catalog);
    assertIterableEquals(Collections.singleton(invalidStreamName), invalidStreamNames);
  }

  @Test
  void testGetFieldNames() throws IOException {
    JsonNode node = Jsons.deserialize(MoreResources.readResource("valid_schema.json"));
    Set<String> actualFieldNames = CatalogHelpers.getAllFieldNames(node);
    Set<String> expectedFieldNames = ImmutableSet.of("date", "CAD", "HKD", "ISK", "PHP", "DKK", "HUF", "文", "somekey", "something", "nestedkey");

    assertEquals(expectedFieldNames, actualFieldNames);
  }

  @Test
  void testGetInvalidFieldNames() throws IOException {
    final String validStreamName = "Valid_Stream";
    final AirbyteStream validStream = new AirbyteStream();
    validStream.setName(validStreamName);
    JsonNode validSchema = Jsons.deserialize(MoreResources.readResource("valid_schema.json"));
    validStream.setJsonSchema(validSchema);

    final String invalidStreamName = "invalid stream";
    AirbyteStream invalidStream = new AirbyteStream();
    invalidStream.setName(invalidStreamName);
    JsonNode invalidSchema = Jsons.deserialize(MoreResources.readResource("invalid_schema.json"));
    invalidStream.setJsonSchema(invalidSchema);

    AirbyteCatalog catalog = new AirbyteCatalog();
    catalog.setStreams(List.of(validStream, invalidStream));

    Multimap<String, String> streamNameToInvalidFieldNames = CatalogHelpers.getInvalidFieldNames(catalog);
    assertIterableEquals(Collections.singleton(invalidStreamName), streamNameToInvalidFieldNames.keySet());
    assertIterableEquals(ImmutableList.of("\"CZK", "C A D"), streamNameToInvalidFieldNames.get(invalidStreamName));
  }

}
