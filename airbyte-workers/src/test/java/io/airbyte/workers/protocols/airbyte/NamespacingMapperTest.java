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

package io.airbyte.workers.protocols.airbyte;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import org.junit.jupiter.api.Test;

class NamespacingMapperTest {

  private static final String OUTPUT_NAMESPACE = "output_";
  private static final String STREAM_NAME = "user_preferences";
  private static final String FIELD_NAME = "favorite_color";
  private static final ConfiguredAirbyteCatalog CATALOG = CatalogHelpers.createConfiguredAirbyteCatalog(
      STREAM_NAME,
      Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING));
  private static final AirbyteMessage RECORD_MESSAGE = AirbyteMessageUtils.createRecordMessage(STREAM_NAME, FIELD_NAME, "blue");

  @Test
  void test() {
    final NamespacingMapper mapper = new NamespacingMapper(OUTPUT_NAMESPACE);

    final ConfiguredAirbyteCatalog originalCatalog = Jsons.clone(CATALOG);
    final ConfiguredAirbyteCatalog expectedCatalog = CatalogHelpers.createConfiguredAirbyteCatalog(
        OUTPUT_NAMESPACE + STREAM_NAME,
        Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING));
    final ConfiguredAirbyteCatalog actualCatalog = mapper.mapCatalog(CATALOG);

    assertEquals(originalCatalog, CATALOG);
    assertEquals(expectedCatalog, actualCatalog);

    final AirbyteMessage originalMessage = Jsons.clone(RECORD_MESSAGE);
    final AirbyteMessage expectedMessage = AirbyteMessageUtils.createRecordMessage(OUTPUT_NAMESPACE + STREAM_NAME, FIELD_NAME, "blue");
    final AirbyteMessage actualMessage = mapper.mapMessage(RECORD_MESSAGE);

    assertEquals(originalMessage, RECORD_MESSAGE);
    assertEquals(expectedMessage, actualMessage);
  }

  @Test
  void testEmptyNamespace() {
    final NamespacingMapper mapper = new NamespacingMapper(null);

    final ConfiguredAirbyteCatalog originalCatalog = Jsons.clone(CATALOG);
    final ConfiguredAirbyteCatalog expectedCatalog = CatalogHelpers.createConfiguredAirbyteCatalog(
        STREAM_NAME,
        Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING));
    final ConfiguredAirbyteCatalog actualCatalog = mapper.mapCatalog(CATALOG);

    assertEquals(originalCatalog, CATALOG);
    assertEquals(expectedCatalog, actualCatalog);

    final AirbyteMessage originalMessage = Jsons.clone(RECORD_MESSAGE);
    final AirbyteMessage expectedMessage = AirbyteMessageUtils.createRecordMessage(
        STREAM_NAME,
        FIELD_NAME, "blue");
    final AirbyteMessage actualMessage = mapper.mapMessage(RECORD_MESSAGE);

    assertEquals(originalMessage, RECORD_MESSAGE);
    assertEquals(expectedMessage, actualMessage);
  }

}
