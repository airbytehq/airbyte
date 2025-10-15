/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class MssqlCdcHelperTest {

  private static final JsonNode LEGACY_NON_CDC_CONFIG = Jsons.jsonNode(Map.of("replication_method", "STANDARD"));
  private static final JsonNode LEGACY_CDC_CONFIG = Jsons.jsonNode(Map.of("replication_method", "CDC"));

  @Test
  public void testIsCdc() {
    // legacy replication method config before version 0.4.0
    assertFalse(MssqlCdcHelper.isCdc(LEGACY_NON_CDC_CONFIG));
    assertTrue(MssqlCdcHelper.isCdc(LEGACY_CDC_CONFIG));

    // new replication method config since version 0.4.0
    final JsonNode newNonCdc = Jsons.jsonNode(Map.of("replication_method",
        Jsons.jsonNode(Map.of("method", "STANDARD"))));
    assertFalse(MssqlCdcHelper.isCdc(newNonCdc));

    final JsonNode newCdc = Jsons.jsonNode(Map.of("replication_method",
        Jsons.jsonNode(Map.of(
            "method", "CDC"))));
    assertTrue(MssqlCdcHelper.isCdc(newCdc));

    // migration from legacy to new config
    final JsonNode mixNonCdc = Jsons.jsonNode(Map.of(
        "replication_method", Jsons.jsonNode(Map.of("method", "STANDARD")),
        "replication", Jsons.jsonNode(Map.of("replication_type", "CDC"))));
    assertFalse(MssqlCdcHelper.isCdc(mixNonCdc));

    final JsonNode mixCdc = Jsons.jsonNode(Map.of(
        "replication", Jsons.jsonNode(Map.of(
            "replication_type", "Standard")),
        "replication_method", Jsons.jsonNode(Map.of(
            "method", "CDC"))));
    assertTrue(MssqlCdcHelper.isCdc(mixCdc));
  }

  @Test
  public void testGetTableIncludeListSingleTable() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(Collections.singletonList(
            new ConfiguredAirbyteStream()
                .withSyncMode(SyncMode.INCREMENTAL)
                .withStream(new AirbyteStream()
                    .withNamespace("dbo")
                    .withName("users"))));

    final String result = MssqlCdcHelper.getTableIncludeList(catalog);
    // Pattern.quote escapes the period in "dbo.users" to "\Qdbo.users\E"
    assertEquals("\\Qdbo.users\\E", result);
  }

  @Test
  public void testGetTableIncludeListMultipleTables() {
    final List<ConfiguredAirbyteStream> streams = Arrays.asList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withStream(new AirbyteStream()
                .withNamespace("dbo")
                .withName("users")),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withStream(new AirbyteStream()
                .withNamespace("dbo")
                .withName("orders")),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withStream(new AirbyteStream()
                .withNamespace("sales")
                .withName("products")));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(streams);
    final String result = MssqlCdcHelper.getTableIncludeList(catalog);

    // Should generate a comma-separated list of escaped table identifiers
    assertEquals("\\Qdbo.users\\E,\\Qdbo.orders\\E,\\Qsales.products\\E", result);
  }

  @Test
  public void testGetTableIncludeListFiltersNonIncrementalStreams() {
    final List<ConfiguredAirbyteStream> streams = Arrays.asList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withStream(new AirbyteStream()
                .withNamespace("dbo")
                .withName("users")),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withStream(new AirbyteStream()
                .withNamespace("dbo")
                .withName("logs")));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(streams);
    final String result = MssqlCdcHelper.getTableIncludeList(catalog);

    // Should only include INCREMENTAL streams
    assertEquals("\\Qdbo.users\\E", result);
  }

  @Test
  public void testGetTableIncludeListWithSpecialCharactersInTableName() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(Collections.singletonList(
            new ConfiguredAirbyteStream()
                .withSyncMode(SyncMode.INCREMENTAL)
                .withStream(new AirbyteStream()
                    .withNamespace("dbo")
                    .withName("table$with_special-chars"))));

    final String result = MssqlCdcHelper.getTableIncludeList(catalog);
    // Pattern.quote should escape special characters
    assertEquals("\\Qdbo.table$with_special-chars\\E", result);
  }

  @Test
  public void testGetTableIncludeListWithCommaInTableName() {
    final List<ConfiguredAirbyteStream> streams = Arrays.asList(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withStream(new AirbyteStream()
                .withNamespace("dbo")
                .withName("table,with,commas")),
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withStream(new AirbyteStream()
                .withNamespace("dbo")
                .withName("normal_table")));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(streams);
    final String result = MssqlCdcHelper.getTableIncludeList(catalog);

    // Commas in table names should be escaped with backslash
    assertEquals("\\Qdbo.table\\,with\\,commas\\E,\\Qdbo.normal_table\\E", result);
  }

  @Test
  public void testGetTableIncludeListEmptyCatalog() {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(Collections.emptyList());

    final String result = MssqlCdcHelper.getTableIncludeList(catalog);
    assertEquals("", result);
  }

}
