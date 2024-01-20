/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
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

}
