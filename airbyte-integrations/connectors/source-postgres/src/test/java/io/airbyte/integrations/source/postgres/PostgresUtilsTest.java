/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.util.Map;
import org.junit.jupiter.api.Test;

class PostgresUtilsTest {

  @Test
  void testIsCdc() {
    final ObjectNode config = (ObjectNode) Jsons.jsonNode(ImmutableMap.builder().build());
    assertFalse(PostgresUtils.isCdc(config));

    config.set("replication_method", Jsons.jsonNode(ImmutableMap.of(
        "replication_slot", "slot",
        "publication", "ab_pub")));
    assertTrue(PostgresUtils.isCdc(config));
  }

  @Test
  void testGetFirstRecordWaitTime() {
    final JsonNode emptyConfig = Jsons.jsonNode(Map.of("initial_waiting_seconds", 10));
    assertEquals(PostgresUtils.DEFAULT_FIRST_RECORD_WAIT_TIME, PostgresUtils.getFirstRecordWaitTime(emptyConfig));
  }

}
