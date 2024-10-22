/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.cdk.integrations.debezium.internals.DebeziumEventConverter.CDC_LSN;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.testcontainers.shaded.com.google.common.collect.ImmutableList;

class PostgresCatalogHelperTest {

  @Test
  public void testRemoveIncrementalWithoutPk() {
    // no primary key
    final AirbyteStream noPrimaryKeyNoIncremental = new AirbyteStream()
        .withSourceDefinedPrimaryKey(Collections.emptyList())
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    final AirbyteStream noPrimaryKeyWithIncremental = new AirbyteStream()
        .withSourceDefinedPrimaryKey(Collections.emptyList())
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));

    assertEquals(noPrimaryKeyNoIncremental,
        PostgresCatalogHelper.removeIncrementalWithoutPk(Jsons.clone(noPrimaryKeyWithIncremental)));
    assertEquals(noPrimaryKeyNoIncremental,
        PostgresCatalogHelper.removeIncrementalWithoutPk(Jsons.clone(noPrimaryKeyNoIncremental)));

    // with primary key
    final AirbyteStream withPrimaryKeyNoIncremental = new AirbyteStream()
        .withSourceDefinedPrimaryKey(List.of(List.of("id")))
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    final AirbyteStream withPrimaryKeyWithIncremental = new AirbyteStream()
        .withSourceDefinedPrimaryKey(List.of(List.of("id")))
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));

    assertEquals(withPrimaryKeyWithIncremental,
        PostgresCatalogHelper.removeIncrementalWithoutPk(Jsons.clone(withPrimaryKeyWithIncremental)));
    assertEquals(withPrimaryKeyNoIncremental,
        PostgresCatalogHelper.removeIncrementalWithoutPk(Jsons.clone(withPrimaryKeyNoIncremental)));
  }

  @Test
  public void testSetIncrementalToSourceDefined() {
    final AirbyteStream withIncremental = new AirbyteStream()
        .withSourceDefinedCursor(false)
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    assertTrue(PostgresCatalogHelper
        .setIncrementalToSourceDefined(withIncremental)
        .getSourceDefinedCursor());

    final AirbyteStream noIncremental = new AirbyteStream()
        .withSourceDefinedCursor(false)
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    assertFalse(PostgresCatalogHelper
        .setIncrementalToSourceDefined(noIncremental)
        .getSourceDefinedCursor());
  }

  @Test
  public void testSetDefaultCursorFieldForCdc() {
    final AirbyteStream cdcIncrementalStream = new AirbyteStream()
        .withSourceDefinedCursor(true)
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    PostgresCatalogHelper.setDefaultCursorFieldForCdc(cdcIncrementalStream);

    assertTrue(cdcIncrementalStream.getSourceDefinedCursor());
    assertEquals(cdcIncrementalStream.getDefaultCursorField(), ImmutableList.of(CDC_LSN));
  }

  @Test
  public void testAddCdcMetadataColumns() {
    final AirbyteStream before = new AirbyteStream()
        .withJsonSchema(Jsons.jsonNode(Map.of("properties", Jsons.deserialize("{}"))));

    final JsonNode properties = Jsons.jsonNode(Map.of(
        "_ab_cdc_lsn", Jsons.jsonNode(Map.of("type", "number")),
        "_ab_cdc_updated_at", Jsons.jsonNode(Map.of("type", "string")),
        "_ab_cdc_deleted_at", Jsons.jsonNode(Map.of("type", "string"))));
    final AirbyteStream after = new AirbyteStream()
        .withJsonSchema(Jsons.jsonNode(Map.of("properties", properties)));

    assertEquals(after, PostgresCatalogHelper.addCdcMetadataColumns(before));
  }

}
