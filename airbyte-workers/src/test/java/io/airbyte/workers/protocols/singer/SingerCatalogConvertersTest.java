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

package io.airbyte.workers.protocols.singer;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.Schema;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.singer.SingerCatalog;
import io.airbyte.singer.SingerMetadataChild;
import io.airbyte.singer.SingerType;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import org.junit.jupiter.api.Test;

class SingerCatalogConvertersTest {

  @Test
  void applySchemaToDiscoveredCatalog() throws IOException {
    final SingerCatalog catalog =
        Jsons.deserialize(MoreResources.readResource("singer_postgres_catalog.json"), SingerCatalog.class);
    final Schema airbyteSchema =
        Jsons.deserialize(MoreResources.readResource("simple_postgres_catalog_output.json"), StandardDiscoverCatalogOutput.class).getSchema();

    final SingerCatalog actualCatalog =
        SingerCatalogConverters.applySchemaToDiscoveredCatalog(catalog, airbyteSchema);

    final SingerCatalog expectedCatalog =
        Jsons.deserialize(MoreResources.readResource("singer_postgres_catalog.json"), SingerCatalog.class);
    expectedCatalog.getStreams().get(0).getMetadata().get(0).getMetadata().withSelected(true);
    expectedCatalog.getStreams().get(0).getMetadata().get(1).getMetadata().withSelected(true);
    expectedCatalog.getStreams().get(0).getMetadata().get(2).getMetadata().withSelected(true);
    expectedCatalog
        .getStreams()
        .get(0)
        .getMetadata()
        .get(0)
        .getMetadata()
        .withReplicationMethod(SingerMetadataChild.ReplicationMethod.FULL_TABLE);

    assertEquals(expectedCatalog, actualCatalog);
  }

  @Test
  void singerTypeToAirbyte() {
    Arrays.stream(SingerType.values()).forEach(singerType -> assertDoesNotThrow(() -> SingerCatalogConverters.singerTypeToDataType(singerType)));
  }

  @Test
  void toAirbyteSchemaWithUnselectedTable() throws IOException {
    final SingerCatalog catalog =
        Jsons.deserialize(MoreResources.readResource("singer_postgres_catalog.json"), SingerCatalog.class);
    final Schema expectedSchema =
        Jsons.deserialize(MoreResources.readResource("simple_postgres_catalog_output.json"), StandardDiscoverCatalogOutput.class).getSchema();
    expectedSchema.getStreams().get(0).withSelected(false);
    expectedSchema.getStreams().get(0).getFields().get(0).withSelected(true);
    expectedSchema.getStreams().get(0).getFields().get(1).withSelected(true);

    final Schema actualSchema = SingerCatalogConverters.toAirbyteSchema(catalog);

    assertEquals(expectedSchema, actualSchema);
  }

  @Test
  void toAirbyteSchemaWithSelectedTable() throws IOException {
    final SingerCatalog catalog =
        Jsons.deserialize(MoreResources.readResource("singer_postgres_catalog.json"), SingerCatalog.class);
    catalog.getStreams().get(0).getMetadata().get(0).getMetadata().withSelected(true);

    final Schema expectedSchema =
        Jsons.deserialize(MoreResources.readResource("simple_postgres_catalog_output.json"), StandardDiscoverCatalogOutput.class).getSchema();
    expectedSchema.getStreams().get(0).withSelected(true);
    expectedSchema.getStreams().get(0).getFields().get(0).withSelected(true);
    expectedSchema.getStreams().get(0).getFields().get(1).withSelected(true);

    final Schema actualSchema = SingerCatalogConverters.toAirbyteSchema(catalog);

    assertEquals(expectedSchema, actualSchema);
  }

  @Test
  void toAirbyteSchemaNoMetadataInSingerCatalog() throws IOException {
    final SingerCatalog catalog =
        Jsons.deserialize(MoreResources.readResource("singer_postgres_catalog.json"), SingerCatalog.class);
    // remove metadata from singer catalog
    catalog.getStreams().forEach(stream -> stream.setMetadata(new ArrayList<>()));
    final Schema expectedSchema =
        Jsons.deserialize(MoreResources.readResource("simple_postgres_catalog_output.json"), StandardDiscoverCatalogOutput.class).getSchema();
    expectedSchema.getStreams().get(0).withSelected(false);
    expectedSchema.getStreams().get(0).getFields().get(0).withSelected(false);
    expectedSchema.getStreams().get(0).getFields().get(1).withSelected(false);

    final Schema actualSchema = SingerCatalogConverters.toAirbyteSchema(catalog);

    assertEquals(expectedSchema, actualSchema);
  }

}
