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
import io.airbyte.db.jdbc.JdbcUtils;
import java.time.Duration;
import java.util.Collections;
import java.util.List;
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

  @Test
  public void shouldFlushAfterSync() {
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", "replication_slot")
        .put("publication", "PUBLICATION")
        .put("plugin", "pgoutput")
        .put("initial_waiting_seconds", 5)
        .put("lsn_commit_behaviour", "After loading Data in the destination")
        .build());

    final JsonNode config = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, "host")
        .put(JdbcUtils.PORT_KEY, 5432)
        .put(JdbcUtils.DATABASE_KEY, "dbName")
        .put(JdbcUtils.SCHEMAS_KEY, List.of("MODELS_SCHEMA", "MODELS_SCHEMA" + "_random"))
        .put(JdbcUtils.USERNAME_KEY, "user")
        .put(JdbcUtils.PASSWORD_KEY, "password")
        .put(JdbcUtils.SSL_KEY, false)
        .put("replication_method", replicationMethod)
        .build());
    assertTrue(PostgresUtils.shouldFlushAfterSync(config));

    final JsonNode replicationMethod2 = ((ObjectNode) replicationMethod)
        .put("lsn_commit_behaviour", "While reading Data");
    ((ObjectNode) config).put("replication_method", replicationMethod2);

    assertFalse(PostgresUtils.shouldFlushAfterSync(config));
  }

}
