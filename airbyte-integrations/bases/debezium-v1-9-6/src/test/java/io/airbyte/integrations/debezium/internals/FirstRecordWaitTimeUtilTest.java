/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import static io.airbyte.integrations.debezium.internals.FirstRecordWaitTimeUtil.MAX_FIRST_RECORD_WAIT_TIME;
import static io.airbyte.integrations.debezium.internals.FirstRecordWaitTimeUtil.MIN_FIRST_RECORD_WAIT_TIME;
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

public class FirstRecordWaitTimeUtilTest {

  @Test
  void testGetFirstRecordWaitTime() {
    final JsonNode emptyConfig = Jsons.jsonNode(Collections.emptyMap());
    assertDoesNotThrow(() -> FirstRecordWaitTimeUtil.checkFirstRecordWaitTime(emptyConfig));
    assertEquals(Optional.empty(), FirstRecordWaitTimeUtil.getFirstRecordWaitSeconds(emptyConfig));
    assertEquals(FirstRecordWaitTimeUtil.DEFAULT_FIRST_RECORD_WAIT_TIME, FirstRecordWaitTimeUtil.getFirstRecordWaitTime(emptyConfig));

    final JsonNode normalConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", 500)));
    assertDoesNotThrow(() -> FirstRecordWaitTimeUtil.checkFirstRecordWaitTime(normalConfig));
    assertEquals(Optional.of(500), FirstRecordWaitTimeUtil.getFirstRecordWaitSeconds(normalConfig));
    assertEquals(Duration.ofSeconds(500), FirstRecordWaitTimeUtil.getFirstRecordWaitTime(normalConfig));

    final int tooShortTimeout = (int) MIN_FIRST_RECORD_WAIT_TIME.getSeconds() - 1;
    final JsonNode tooShortConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooShortTimeout)));
    assertThrows(IllegalArgumentException.class, () -> FirstRecordWaitTimeUtil.checkFirstRecordWaitTime(tooShortConfig));
    assertEquals(Optional.of(tooShortTimeout), FirstRecordWaitTimeUtil.getFirstRecordWaitSeconds(tooShortConfig));
    assertEquals(MIN_FIRST_RECORD_WAIT_TIME, FirstRecordWaitTimeUtil.getFirstRecordWaitTime(tooShortConfig));

    final int tooLongTimeout = (int) MAX_FIRST_RECORD_WAIT_TIME.getSeconds() + 1;
    final JsonNode tooLongConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooLongTimeout)));
    assertThrows(IllegalArgumentException.class, () -> FirstRecordWaitTimeUtil.checkFirstRecordWaitTime(tooLongConfig));
    assertEquals(Optional.of(tooLongTimeout), FirstRecordWaitTimeUtil.getFirstRecordWaitSeconds(tooLongConfig));
    assertEquals(MAX_FIRST_RECORD_WAIT_TIME, FirstRecordWaitTimeUtil.getFirstRecordWaitTime(tooLongConfig));
  }

}
