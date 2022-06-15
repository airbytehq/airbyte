package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.SyncMode;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class PostgresCdcCatalogHelperTest {

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
        PostgresCdcCatalogHelper.removeIncrementalWithoutPk(Jsons.clone(noPrimaryKeyWithIncremental)));
    assertEquals(noPrimaryKeyNoIncremental,
        PostgresCdcCatalogHelper.removeIncrementalWithoutPk(Jsons.clone(noPrimaryKeyNoIncremental)));

    // with primary key
    final AirbyteStream withPrimaryKeyNoIncremental = new AirbyteStream()
        .withSourceDefinedPrimaryKey(List.of(List.of("id")))
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    final AirbyteStream withPrimaryKeyWithIncremental = new AirbyteStream()
        .withSourceDefinedPrimaryKey(List.of(List.of("id")))
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));

    assertEquals(withPrimaryKeyWithIncremental,
        PostgresCdcCatalogHelper.removeIncrementalWithoutPk(Jsons.clone(withPrimaryKeyWithIncremental)));
    assertEquals(withPrimaryKeyNoIncremental,
        PostgresCdcCatalogHelper.removeIncrementalWithoutPk(Jsons.clone(withPrimaryKeyNoIncremental)));
  }

  @Test
  public void testSetIncrementalToSourceDefined() {
    final AirbyteStream withIncremental = new AirbyteStream()
        .withSourceDefinedCursor(false)
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));
    assertTrue(PostgresCdcCatalogHelper
        .setIncrementalToSourceDefined(withIncremental)
        .getSourceDefinedCursor());

    final AirbyteStream noIncremental = new AirbyteStream()
        .withSourceDefinedCursor(false)
        .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH));
    assertFalse(PostgresCdcCatalogHelper
        .setIncrementalToSourceDefined(noIncremental)
        .getSourceDefinedCursor());
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

    assertEquals(after, PostgresCdcCatalogHelper.addCdcMetadataColumns(before));
  }

}
