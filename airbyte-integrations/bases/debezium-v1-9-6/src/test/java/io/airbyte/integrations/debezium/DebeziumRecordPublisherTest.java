/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.collect.ImmutableList;
import io.airbyte.integrations.debezium.internals.DebeziumPropertiesManager;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.regex.Pattern;
import org.junit.jupiter.api.Test;

class DebeziumRecordPublisherTest {

  @Test
  public void testTableIncludelistCreation() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(ImmutableList.of(
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name", "public").withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("id_,something", "public").withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("n\"aMéS", "public").withSyncMode(SyncMode.INCREMENTAL)));

    final String expectedWhitelist = "\\Qpublic.id_and_name\\E,\\Qpublic.id_\\,something\\E,\\Qpublic.n\"aMéS\\E";
    final String actualWhitelist = DebeziumPropertiesManager.getTableIncludelist(catalog);

    assertEquals(expectedWhitelist, actualWhitelist);
  }

  @Test
  public void testTableIncludelistFiltersFullRefresh() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(ImmutableList.of(
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name", "public").withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name2", "public").withSyncMode(SyncMode.FULL_REFRESH)));

    final String expectedWhitelist = "\\Qpublic.id_and_name\\E";
    final String actualWhitelist = DebeziumPropertiesManager.getTableIncludelist(catalog);

    assertEquals(expectedWhitelist, actualWhitelist);
  }

  @Test
  public void testColumnIncludelistFiltersFullRefresh() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(ImmutableList.of(
        CatalogHelpers.createConfiguredAirbyteStream(
            "id_and_name",
            "public",
            Field.of("fld1", JsonSchemaType.NUMBER), Field.of("fld2", JsonSchemaType.STRING)).withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("id_,something", "public").withSyncMode(SyncMode.INCREMENTAL),
        CatalogHelpers.createConfiguredAirbyteStream("id_and_name2", "public").withSyncMode(SyncMode.FULL_REFRESH),
        CatalogHelpers.createConfiguredAirbyteStream("n\"aMéS", "public").withSyncMode(SyncMode.INCREMENTAL)));

    final String expectedWhitelist = "\\Qpublic.id_and_name\\E\\.(\\Qfld2\\E|\\Qfld1\\E),\\Qpublic.id_\\,something\\E,\\Qpublic.n\"aMéS\\E";
    final String actualWhitelist = DebeziumPropertiesManager.getColumnIncludeList(catalog);

    assertEquals(expectedWhitelist, actualWhitelist);
  }

  @Test
  public void testColumnIncludeListEscaping() {
    // final String a = "public\\.products\\*\\^\\$\\+-\\\\";
    // final String b = "public.products*^$+-\\";
    // final Pattern p = Pattern.compile(a, Pattern.UNIX_LINES);
    // assertTrue(p.matcher(b).find());
    // assertTrue(Pattern.compile(Pattern.quote(b)).matcher(b).find());

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(ImmutableList.of(
        CatalogHelpers.createConfiguredAirbyteStream(
            "id_and_name",
            "public",
            Field.of("fld1", JsonSchemaType.NUMBER), Field.of("fld2", JsonSchemaType.STRING)).withSyncMode(SyncMode.INCREMENTAL)));

    final String anchored = "^" + DebeziumPropertiesManager.getColumnIncludeList(catalog) + "$";
    final Pattern pattern = Pattern.compile(anchored);

    assertTrue(pattern.matcher("public.id_and_name.fld1").find());
    assertTrue(pattern.matcher("public.id_and_name.fld2").find());
    assertFalse(pattern.matcher("ic.id_and_name.fl").find());
    assertFalse(pattern.matcher("ppppublic.id_and_name.fld2333").find());
    assertFalse(pattern.matcher("public.id_and_name.fld_wrong_wrong").find());
  }

}
