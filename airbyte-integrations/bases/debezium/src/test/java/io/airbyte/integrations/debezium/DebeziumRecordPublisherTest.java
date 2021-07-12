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

package io.airbyte.integrations.debezium;

import static org.junit.jupiter.api.Assertions.*;

import com.google.common.collect.ImmutableList;
import io.airbyte.integrations.debezium.internals.DebeziumRecordPublisher;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.SyncMode;
import org.junit.jupiter.api.Test;

class DebeziumRecordPublisherTest {

  @Test
  public void testWhitelistCreation() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(ImmutableList.of(
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name", "public").withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("id_,something", "public").withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("n\"aMéS", "public").withSyncMode(SyncMode.INCREMENTAL)));

    final String expectedWhitelist = "public.id_and_name,public.id_\\,something,public.n\"aMéS";
    final String actualWhitelist = DebeziumRecordPublisher.getTableWhitelist(catalog);

    assertEquals(expectedWhitelist, actualWhitelist);
  }

  @Test
  public void testWhitelistFiltersFullRefresh() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(ImmutableList.of(
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name", "public").withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name2", "public").withSyncMode(SyncMode.FULL_REFRESH)));

    final String expectedWhitelist = "public.id_and_name";
    final String actualWhitelist = DebeziumRecordPublisher.getTableWhitelist(catalog);

    assertEquals(expectedWhitelist, actualWhitelist);
  }

}
