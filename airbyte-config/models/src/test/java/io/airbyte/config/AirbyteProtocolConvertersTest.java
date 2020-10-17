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

package io.airbyte.config;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.Lists;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import org.junit.jupiter.api.Test;

class AirbyteProtocolConvertersTest {

  private static final String STREAM = "users";
  private static final String COLUMN_NAME = "name";
  private static final String COLUMN_AGE = "age";
  private static final AirbyteCatalog CATALOG = new AirbyteCatalog()
      .withStreams(Lists.newArrayList(new AirbyteStream()
          .withName(STREAM)
          .withJsonSchema(CatalogHelpers.fieldsToJsonSchema(
              Field.of(COLUMN_NAME, JsonSchemaPrimitive.STRING),
              Field.of(COLUMN_AGE, JsonSchemaPrimitive.NUMBER)))));

  private static final Schema SCHEMA = new Schema()
      .withStreams(Lists.newArrayList(new Stream()
          .withName(STREAM)
          .withFields(Lists.newArrayList(
              new io.airbyte.config.Field()
                  .withName(COLUMN_NAME)
                  .withDataType(DataType.STRING)
                  .withSelected(true),
              new io.airbyte.config.Field()
                  .withName(COLUMN_AGE)
                  .withDataType(DataType.NUMBER)
                  .withSelected(true)))));

  @Test
  void testToCatalog() {
    assertEquals(CATALOG, AirbyteProtocolConverters.toCatalog(SCHEMA));
  }

  @Test
  void testToSchema() {
    assertEquals(SCHEMA, AirbyteProtocolConverters.toSchema(CATALOG));
  }

}
