/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.MssqlCdcHelper.DataToSync;
import io.airbyte.integrations.source.mssql.MssqlCdcHelper.SnapshotIsolation;
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
            "method", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Snapshot"))));
    assertTrue(MssqlCdcHelper.isCdc(newCdc));

    // migration from legacy to new config
    final JsonNode mixNonCdc = Jsons.jsonNode(Map.of(
        "replication_method", Jsons.jsonNode(Map.of("method", "STANDARD")),
        "replication", Jsons.jsonNode(Map.of("replication_type", "CDC"))));
    assertFalse(MssqlCdcHelper.isCdc(mixNonCdc));

    final JsonNode mixCdc = Jsons.jsonNode(Map.of(
        "replication", Jsons.jsonNode(Map.of(
            "replication_type", "Standard",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Snapshot")),
        "replication_method", Jsons.jsonNode(Map.of(
            "method", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Snapshot"))));
    assertTrue(MssqlCdcHelper.isCdc(mixCdc));
  }

  @Test
  public void testGetSnapshotIsolation() {
    // legacy replication method config before version 0.4.0
    assertEquals(SnapshotIsolation.SNAPSHOT, MssqlCdcHelper.getSnapshotIsolationConfig(LEGACY_CDC_CONFIG));

    // new replication method config since version 0.4.0
    final JsonNode newCdcNonSnapshot = Jsons.jsonNode(Map.of("replication",
        Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Read Committed"))));
    assertEquals(SnapshotIsolation.READ_COMMITTED, MssqlCdcHelper.getSnapshotIsolationConfig(newCdcNonSnapshot));

    final JsonNode newCdcSnapshot = Jsons.jsonNode(Map.of("replication",
        Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Snapshot"))));
    assertEquals(SnapshotIsolation.SNAPSHOT, MssqlCdcHelper.getSnapshotIsolationConfig(newCdcSnapshot));

    // migration from legacy to new config
    final JsonNode mixCdcNonSnapshot = Jsons.jsonNode(Map.of(
        "replication_method", "Standard",
        "replication", Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Read Committed"))));
    assertEquals(SnapshotIsolation.READ_COMMITTED, MssqlCdcHelper.getSnapshotIsolationConfig(mixCdcNonSnapshot));

    final JsonNode mixCdcSnapshot = Jsons.jsonNode(Map.of(
        "replication_method", "Standard",
        "replication", Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Snapshot"))));
    assertEquals(SnapshotIsolation.SNAPSHOT, MssqlCdcHelper.getSnapshotIsolationConfig(mixCdcSnapshot));
  }

  @Test
  public void testGetDataToSyncConfig() {
    // legacy replication method config before version 0.4.0
    assertEquals(DataToSync.EXISTING_AND_NEW, MssqlCdcHelper.getDataToSyncConfig(LEGACY_CDC_CONFIG));

    // new replication method config since version 0.4.0
    final JsonNode newCdcExistingAndNew = Jsons.jsonNode(Map.of("replication",
        Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Read Committed"))));
    assertEquals(DataToSync.EXISTING_AND_NEW, MssqlCdcHelper.getDataToSyncConfig(newCdcExistingAndNew));

    final JsonNode newCdcNewOnly = Jsons.jsonNode(Map.of("replication",
        Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "New Changes Only",
            "snapshot_isolation", "Snapshot"))));
    assertEquals(DataToSync.NEW_CHANGES_ONLY, MssqlCdcHelper.getDataToSyncConfig(newCdcNewOnly));

    final JsonNode mixCdcExistingAndNew = Jsons.jsonNode(Map.of(
        "replication_method", "Standard",
        "replication", Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "Existing and New",
            "snapshot_isolation", "Read Committed"))));
    assertEquals(DataToSync.EXISTING_AND_NEW, MssqlCdcHelper.getDataToSyncConfig(mixCdcExistingAndNew));

    final JsonNode mixCdcNewOnly = Jsons.jsonNode(Map.of(
        "replication_method", "Standard",
        "replication",
        Jsons.jsonNode(Map.of(
            "replication_type", "CDC",
            "data_to_sync", "New Changes Only",
            "snapshot_isolation", "Snapshot"))));
    assertEquals(DataToSync.NEW_CHANGES_ONLY, MssqlCdcHelper.getDataToSyncConfig(mixCdcNewOnly));
  }

}
