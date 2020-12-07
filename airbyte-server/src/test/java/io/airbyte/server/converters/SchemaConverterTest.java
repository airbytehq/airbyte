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

import com.google.common.collect.Lists;
import io.airbyte.api.model.SourceSchema;
import io.airbyte.api.model.SourceSchemaField;
import io.airbyte.api.model.SourceSchemaStream;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.DataType;
import io.airbyte.config.Field;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardSync.SyncMode;
import io.airbyte.config.Stream;
import org.junit.jupiter.api.Test;

class SchemaConverterTest {

  private static final String STREAM_NAME = "users";
  private static final String COLUMN_ID = "id";
  private static final Schema SCHEMA = new Schema()
      .withStreams(Lists.newArrayList(new Stream()
          .withName(STREAM_NAME)
          .withSelected(true)
          .withFields(Lists.newArrayList(new Field()
              .withDataType(DataType.STRING)
              .withName(COLUMN_ID)
              .withName(COLUMN_ID)
              .withSelected(true)))
          .withSourceDefinedCursor(false)
          .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
          .withDefaultCursorField(Lists.newArrayList(COLUMN_ID))
          .withSyncMode(SyncMode.INCREMENTAL)
          .withCursorField(Lists.newArrayList(COLUMN_ID))));

  private static final SourceSchema API_SCHEMA = new SourceSchema()
      .streams(Lists.newArrayList(new SourceSchemaStream()
          .name(STREAM_NAME)
          .cleanedName(STREAM_NAME)
          .fields(Lists.newArrayList(new SourceSchemaField()
              .dataType(io.airbyte.api.model.DataType.STRING)
              .name(COLUMN_ID)
              .cleanedName(COLUMN_ID)
              .selected(true)))
          .sourceDefinedCursor(false)
          .supportedSyncModes(Lists.newArrayList(io.airbyte.api.model.SyncMode.FULL_REFRESH, io.airbyte.api.model.SyncMode.INCREMENTAL))
          .defaultCursorField(Lists.newArrayList(COLUMN_ID))
          .syncMode(io.airbyte.api.model.SyncMode.INCREMENTAL)
          .cursorField(Lists.newArrayList(COLUMN_ID))));

  @Test
  void convertToPersistenceSchema() {
    assertEquals(SCHEMA, SchemaConverter.toPersistenceSchema(API_SCHEMA));
  }

  @Test
  void convertToApiSchema() {
    assertEquals(API_SCHEMA, SchemaConverter.toApiSchema(SCHEMA));
  }

  @Test
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(io.airbyte.api.model.DataType.class, DataType.class));
    assertTrue(Enums.isCompatible(io.airbyte.config.StandardSync.SyncMode.class, io.airbyte.api.model.SyncMode.class));
  }

}
