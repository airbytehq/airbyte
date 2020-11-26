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
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.Field.JsonSchemaPrimitive;
import io.airbyte.protocol.models.SyncMode;
import java.util.Collections;
import org.junit.jupiter.api.Test;

class AirbyteProtocolConvertersTest {

  private static final String STREAM = "users";
  private static final String STREAM_2 = "users2";
  private static final String COLUMN_NAME = "name";
  private static final String COLUMN_AGE = "age";

  private static final AirbyteStream AB_STREAM = new AirbyteStream()
      .withName(STREAM)
      .withJsonSchema(CatalogHelpers.fieldsToJsonSchema(
          Field.of(COLUMN_NAME, JsonSchemaPrimitive.STRING),
          Field.of(COLUMN_AGE, JsonSchemaPrimitive.NUMBER)))
      .withSourceDefinedCursor(false)
      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
      .withDefaultCursorField(Lists.newArrayList(COLUMN_AGE));

  private static final AirbyteCatalog CATALOG = new AirbyteCatalog().withStreams(Lists.newArrayList(AB_STREAM));

  private static final ConfiguredAirbyteCatalog CONFIGURED_CATALOG = new ConfiguredAirbyteCatalog()
      .withStreams(Lists.newArrayList(new ConfiguredAirbyteStream()
          .withStream(AB_STREAM)
          .withSyncMode(SyncMode.INCREMENTAL)
          .withCursorField(Lists.newArrayList(COLUMN_NAME))));

  private static final Schema SCHEMA = new Schema()
      .withStreams(Lists.newArrayList(new Stream()
          .withSelected(true)
          .withName(STREAM)
          .withFields(Lists.newArrayList(
              new io.airbyte.config.Field()
                  .withName(COLUMN_NAME)
                  .withDataType(DataType.STRING),
              new io.airbyte.config.Field()
                  .withName(COLUMN_AGE)
                  .withDataType(DataType.NUMBER)))
          .withSourceDefinedCursor(false)
          .withSupportedSyncModes(Lists.newArrayList(StandardSync.SyncMode.FULL_REFRESH, StandardSync.SyncMode.INCREMENTAL))
          .withDefaultCursorField(Lists.newArrayList(COLUMN_AGE))));

  private static final Schema SCHEMA_WITH_UNSELECTED = new Schema()
      .withStreams(Lists.newArrayList(new Stream()
          .withSelected(true)
          .withName(STREAM)
          .withFields(Lists.newArrayList(
              new io.airbyte.config.Field()
                  .withName(COLUMN_NAME)
                  .withDataType(DataType.STRING),
              new io.airbyte.config.Field()
                  .withName(COLUMN_AGE)
                  .withDataType(DataType.NUMBER)))
          .withSourceDefinedCursor(false)
          .withSupportedSyncModes(Lists.newArrayList(StandardSync.SyncMode.FULL_REFRESH, StandardSync.SyncMode.INCREMENTAL))
          .withDefaultCursorField(Lists.newArrayList(COLUMN_AGE)),
          new Stream()
              .withName(STREAM_2)
              .withFields(Lists.newArrayList(
                  new io.airbyte.config.Field()
                      .withName(COLUMN_NAME)
                      .withDataType(DataType.STRING),
                  new io.airbyte.config.Field()
                      .withName(COLUMN_AGE)
                      .withDataType(DataType.NUMBER)))));

  @Test
  void testToConfiguredCatalog() {
    final Schema schema = Jsons.clone(SCHEMA);
    schema.getStreams().get(0).withCursorField(Lists.newArrayList(COLUMN_NAME));
    schema.getStreams().get(0).withSyncMode(StandardSync.SyncMode.INCREMENTAL);
    assertEquals(CONFIGURED_CATALOG, AirbyteProtocolConverters.toConfiguredCatalog(schema));
  }

  // the stream that is input is a schema with 2 streams, but only one is selected. so the expected
  // output is the same the case for the schema with just one selected stream.
  @Test
  void testToConfiguredCatalogWithUnselectedStream() {
    final Schema schema = Jsons.clone(SCHEMA_WITH_UNSELECTED);
    schema.getStreams().get(0).withCursorField(Lists.newArrayList(COLUMN_NAME));
    schema.getStreams().get(0).withSyncMode(StandardSync.SyncMode.INCREMENTAL);
    assertEquals(CONFIGURED_CATALOG, AirbyteProtocolConverters.toConfiguredCatalog(schema));
  }

  @Test
  void testToSchema() {
    assertEquals(SCHEMA, AirbyteProtocolConverters.toSchema(CATALOG));
  }

  @Test
  void testToSchemaWithMultipleJsonSchemaTypesAndFormats() {
    final AirbyteCatalog catalog =
        CatalogHelpers.createAirbyteCatalog(STREAM, Field.of("date", JsonSchemaPrimitive.STRING), Field.of(COLUMN_AGE, JsonSchemaPrimitive.NUMBER));
    final Schema schema = new Schema()
        .withStreams(Lists.newArrayList(new Stream()
            .withName(STREAM)
            .withFields(Lists.newArrayList(
                new io.airbyte.config.Field()
                    .withName("date")
                    .withDataType(DataType.STRING),
                new io.airbyte.config.Field()
                    .withName(COLUMN_AGE)
                    .withDataType(DataType.NUMBER)))
            .withSelected(true)));

    assertEquals(schema, AirbyteProtocolConverters.toSchema(catalog));
  }

  @Test
  void testAnyOfAsObject() {
    final String testString =
        "{\"streams\":[{\"name\":\"users\",\"json_schema\":{\"properties\":{\"date\":{\"anyOf\":[{\"type\":\"string\"},{\"type\":\"object\"}]}}}}]}";

    final Schema schema = new Schema()
        .withStreams(Lists.newArrayList(new Stream()
            .withName(STREAM)
            .withFields(Lists.newArrayList(
                new io.airbyte.config.Field()
                    .withName("date")
                    .withDataType(DataType.OBJECT)))
            .withSelected(true)));

    final AirbyteCatalog catalog = Jsons.deserialize(testString, AirbyteCatalog.class);
    assertEquals(schema, AirbyteProtocolConverters.toSchema(catalog));
  }

  @Test
  void testStreamWithNoFields() {
    final Schema schema = Jsons.clone(SCHEMA);
    schema.getStreams().get(0).withCursorField(Lists.newArrayList(COLUMN_NAME));
    schema.getStreams().get(0).withSyncMode(StandardSync.SyncMode.INCREMENTAL);
    schema.getStreams().get(0).setFields(Lists.newArrayList());
    final ConfiguredAirbyteCatalog actualCatalog = AirbyteProtocolConverters.toConfiguredCatalog(schema);

    final ConfiguredAirbyteCatalog expectedCatalog = Jsons.clone(CONFIGURED_CATALOG);
    ((ObjectNode) expectedCatalog.getStreams().get(0).getStream().getJsonSchema()).set("properties", Jsons.jsonNode(Collections.emptyMap()));

    assertEquals(expectedCatalog, actualCatalog);
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(io.airbyte.protocol.models.SyncMode.class, io.airbyte.config.StandardSync.SyncMode.class));
  }

}
