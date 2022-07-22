/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.PostgresUtils.MAX_FIRST_RECORD_WAIT_TIME;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.time.Duration;
import java.util.Collections;
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
    final JsonNode emptyConfig = Jsons.jsonNode(Collections.emptyMap());
    assertEquals(PostgresUtils.DEFAULT_FIRST_RECORD_WAIT_TIME, PostgresUtils.getFirstRecordWaitTime(emptyConfig));

    final JsonNode normalConfig = Jsons.jsonNode(Map.of("initial_waiting_seconds", 500));
    assertEquals(Duration.ofSeconds(500), PostgresUtils.getFirstRecordWaitTime(normalConfig));

    final JsonNode tooLongConfig = Jsons.jsonNode(Map.of("initial_waiting_seconds", MAX_FIRST_RECORD_WAIT_TIME.getSeconds() + 100));
    assertEquals(MAX_FIRST_RECORD_WAIT_TIME, PostgresUtils.getFirstRecordWaitTime(tooLongConfig));
  }

}
