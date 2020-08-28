/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.workers.singer;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.dataline.config.Schema;
import io.dataline.config.SingerCatalog;
import io.dataline.config.SingerMetadataChild;
import io.dataline.config.StandardDiscoverSchemaOutput;
import io.dataline.workers.BaseWorkerTestCase;
import java.io.IOException;
import org.junit.jupiter.api.Test;

class SingerCatalogConvertersTest extends BaseWorkerTestCase {

  @Test
  void applySchemaToDiscoveredCatalog() throws IOException {
    final SingerCatalog catalog =
        readAs("simple_postgres_singer_catalog.json", SingerCatalog.class);
    final Schema datalineSchema =
        readAs("simple_postgres_schema.json", StandardDiscoverSchemaOutput.class).getSchema();

    final SingerCatalog actualCatalog =
        SingerCatalogConverters.applySchemaToDiscoveredCatalog(catalog, datalineSchema);

    final SingerCatalog expectedCatalog =
        readAs("simple_postgres_singer_catalog.json", SingerCatalog.class);
    expectedCatalog.getStreams().get(0).getMetadata().get(0).getMetadata().setSelected(true);
    expectedCatalog.getStreams().get(0).getMetadata().get(1).getMetadata().setSelected(true);
    expectedCatalog.getStreams().get(0).getMetadata().get(2).getMetadata().setSelected(true);
    expectedCatalog
        .getStreams()
        .get(0)
        .getMetadata()
        .get(0)
        .getMetadata()
        .setReplicationMethod(SingerMetadataChild.ReplicationMethod.FULL_TABLE);

    assertEquals(expectedCatalog, actualCatalog);
  }

  @Test
  void toDatalineSchemaWithUnselectedTable() throws IOException {
    final SingerCatalog catalog =
        readAs("simple_postgres_singer_catalog.json", SingerCatalog.class);
    final Schema expectedSchema =
        readAs("simple_postgres_schema.json", StandardDiscoverSchemaOutput.class).getSchema();
    expectedSchema.getTables().get(0).setSelected(false);
    expectedSchema.getTables().get(0).getColumns().get(0).setSelected(true);
    expectedSchema.getTables().get(0).getColumns().get(1).setSelected(true);

    final Schema actualSchema = SingerCatalogConverters.toDatalineSchema(catalog);

    assertEquals(expectedSchema, actualSchema);
  }

  @Test
  void toDatalineSchemaWithSelectedTable() throws IOException {
    final SingerCatalog catalog =
        readAs("simple_postgres_singer_catalog.json", SingerCatalog.class);
    catalog.getStreams().get(0).getMetadata().get(0).getMetadata().setSelected(true);

    final Schema expectedSchema =
        readAs("simple_postgres_schema.json", StandardDiscoverSchemaOutput.class).getSchema();
    expectedSchema.getTables().get(0).setSelected(true);
    expectedSchema.getTables().get(0).getColumns().get(0).setSelected(true);
    expectedSchema.getTables().get(0).getColumns().get(1).setSelected(true);

    final Schema actualSchema = SingerCatalogConverters.toDatalineSchema(catalog);

    assertEquals(expectedSchema, actualSchema);
  }
}
