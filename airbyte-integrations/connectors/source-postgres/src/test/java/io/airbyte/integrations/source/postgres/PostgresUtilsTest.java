/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static io.airbyte.integrations.source.postgres.PostgresUtils.MAX_FIRST_RECORD_WAIT_TIME;
import static io.airbyte.integrations.source.postgres.PostgresUtils.MIN_FIRST_RECORD_WAIT_TIME;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import java.time.Duration;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
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
    assertDoesNotThrow(() -> PostgresUtils.checkFirstRecordWaitTime(emptyConfig));
    assertEquals(Optional.empty(), PostgresUtils.getFirstRecordWaitSeconds(emptyConfig));
    assertEquals(PostgresUtils.DEFAULT_FIRST_RECORD_WAIT_TIME, PostgresUtils.getFirstRecordWaitTime(emptyConfig));

    final JsonNode normalConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", 500)));
    assertDoesNotThrow(() -> PostgresUtils.checkFirstRecordWaitTime(normalConfig));
    assertEquals(Optional.of(500), PostgresUtils.getFirstRecordWaitSeconds(normalConfig));
    assertEquals(Duration.ofSeconds(500), PostgresUtils.getFirstRecordWaitTime(normalConfig));

    final int tooShortTimeout = (int) MIN_FIRST_RECORD_WAIT_TIME.getSeconds() - 1;
    final JsonNode tooShortConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooShortTimeout)));
    assertThrows(IllegalArgumentException.class, () -> PostgresUtils.checkFirstRecordWaitTime(tooShortConfig));
    assertEquals(Optional.of(tooShortTimeout), PostgresUtils.getFirstRecordWaitSeconds(tooShortConfig));
    assertEquals(MIN_FIRST_RECORD_WAIT_TIME, PostgresUtils.getFirstRecordWaitTime(tooShortConfig));

    final int tooLongTimeout = (int) MAX_FIRST_RECORD_WAIT_TIME.getSeconds() + 1;
    final JsonNode tooLongConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooLongTimeout)));
    assertThrows(IllegalArgumentException.class, () -> PostgresUtils.checkFirstRecordWaitTime(tooLongConfig));
    assertEquals(Optional.of(tooLongTimeout), PostgresUtils.getFirstRecordWaitSeconds(tooLongConfig));
    assertEquals(MAX_FIRST_RECORD_WAIT_TIME, PostgresUtils.getFirstRecordWaitTime(tooLongConfig));
  }

}
