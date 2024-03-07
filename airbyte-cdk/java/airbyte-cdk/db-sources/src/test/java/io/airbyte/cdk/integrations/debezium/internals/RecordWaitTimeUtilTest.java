/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import static io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil.MAX_FIRST_RECORD_WAIT_TIME;
import static io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil.MIN_FIRST_RECORD_WAIT_TIME;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.time.Duration;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

public class RecordWaitTimeUtilTest {

  @Test
  void testGetFirstRecordWaitTime() {
    final JsonNode emptyConfig = Jsons.jsonNode(Collections.emptyMap());
    assertDoesNotThrow(() -> RecordWaitTimeUtil.checkFirstRecordWaitTime(emptyConfig));
    assertEquals(Optional.empty(), RecordWaitTimeUtil.getFirstRecordWaitSeconds(emptyConfig));
    assertEquals(RecordWaitTimeUtil.DEFAULT_FIRST_RECORD_WAIT_TIME, RecordWaitTimeUtil.getFirstRecordWaitTime(emptyConfig));

    final JsonNode normalConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", 500)));
    assertDoesNotThrow(() -> RecordWaitTimeUtil.checkFirstRecordWaitTime(normalConfig));
    assertEquals(Optional.of(500), RecordWaitTimeUtil.getFirstRecordWaitSeconds(normalConfig));
    assertEquals(Duration.ofSeconds(500), RecordWaitTimeUtil.getFirstRecordWaitTime(normalConfig));

    final int tooShortTimeout = (int) MIN_FIRST_RECORD_WAIT_TIME.getSeconds() - 1;
    final JsonNode tooShortConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooShortTimeout)));
    assertThrows(IllegalArgumentException.class, () -> RecordWaitTimeUtil.checkFirstRecordWaitTime(tooShortConfig));
    assertEquals(Optional.of(tooShortTimeout), RecordWaitTimeUtil.getFirstRecordWaitSeconds(tooShortConfig));
    assertEquals(MIN_FIRST_RECORD_WAIT_TIME, RecordWaitTimeUtil.getFirstRecordWaitTime(tooShortConfig));

    final int tooLongTimeout = (int) MAX_FIRST_RECORD_WAIT_TIME.getSeconds() + 1;
    final JsonNode tooLongConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooLongTimeout)));
    assertThrows(IllegalArgumentException.class, () -> RecordWaitTimeUtil.checkFirstRecordWaitTime(tooLongConfig));
    assertEquals(Optional.of(tooLongTimeout), RecordWaitTimeUtil.getFirstRecordWaitSeconds(tooLongConfig));
    assertEquals(MAX_FIRST_RECORD_WAIT_TIME, RecordWaitTimeUtil.getFirstRecordWaitTime(tooLongConfig));
  }

}
