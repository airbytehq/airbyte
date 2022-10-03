/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import static org.junit.jupiter.api.Assertions.*;

import com.google.common.collect.ImmutableList;
import io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager;
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
    final String actualWhitelist = DebeziumPropertiesManager.getTableWhitelist(catalog);

    assertEquals(expectedWhitelist, actualWhitelist);
  }

  @Test
  public void testWhitelistFiltersFullRefresh() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(ImmutableList.of(
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name", "public").withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name2", "public").withSyncMode(SyncMode.FULL_REFRESH)));

    final String expectedWhitelist = "public.id_and_name";
    final String actualWhitelist = DebeziumPropertiesManager.getTableWhitelist(catalog);

    assertEquals(expectedWhitelist, actualWhitelist);
  }

}
