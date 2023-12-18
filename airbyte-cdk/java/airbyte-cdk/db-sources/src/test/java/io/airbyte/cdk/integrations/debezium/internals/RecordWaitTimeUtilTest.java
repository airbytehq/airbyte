/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.debezium.internals;

import static io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil.MAX_FIRST_RECORD_WAIT_TIME;
import static io.airbyte.cdk.integrations.debezium.internals.RecordWaitTimeUtil.MIN_FIRST_RECORD_WAIT_TIME;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import io.airbyte.cdk.integrations.config.AirbyteSourceConfig;
import java.time.Duration;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

public class RecordWaitTimeUtilTest {

  @Test
  void testGetFirstRecordWaitTime() {
    final AirbyteSourceConfig emptyConfig = AirbyteSourceConfig.fromNothing();
    assertDoesNotThrow(() -> RecordWaitTimeUtil.checkFirstRecordWaitTime(emptyConfig));
    assertEquals(Optional.empty(), RecordWaitTimeUtil.getFirstRecordWaitSeconds(emptyConfig));
    assertEquals(RecordWaitTimeUtil.DEFAULT_FIRST_RECORD_WAIT_TIME, RecordWaitTimeUtil.getFirstRecordWaitTime(emptyConfig));

    final AirbyteSourceConfig normalConfig = AirbyteSourceConfig.fromMap(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", 500)));
    assertDoesNotThrow(() -> RecordWaitTimeUtil.checkFirstRecordWaitTime(normalConfig));
    assertEquals(Optional.of(500), RecordWaitTimeUtil.getFirstRecordWaitSeconds(normalConfig));
    assertEquals(Duration.ofSeconds(500), RecordWaitTimeUtil.getFirstRecordWaitTime(normalConfig));

    final int tooShortTimeout = (int) MIN_FIRST_RECORD_WAIT_TIME.getSeconds() - 1;
    final AirbyteSourceConfig tooShortConfig = AirbyteSourceConfig.fromMap(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooShortTimeout)));
    assertThrows(IllegalArgumentException.class, () -> RecordWaitTimeUtil.checkFirstRecordWaitTime(tooShortConfig));
    assertEquals(Optional.of(tooShortTimeout), RecordWaitTimeUtil.getFirstRecordWaitSeconds(tooShortConfig));
    assertEquals(MIN_FIRST_RECORD_WAIT_TIME, RecordWaitTimeUtil.getFirstRecordWaitTime(tooShortConfig));

    final int tooLongTimeout = (int) MAX_FIRST_RECORD_WAIT_TIME.getSeconds() + 1;
    final AirbyteSourceConfig tooLongConfig = AirbyteSourceConfig.fromMap(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooLongTimeout)));
    assertThrows(IllegalArgumentException.class, () -> RecordWaitTimeUtil.checkFirstRecordWaitTime(tooLongConfig));
    assertEquals(Optional.of(tooLongTimeout), RecordWaitTimeUtil.getFirstRecordWaitSeconds(tooLongConfig));
    assertEquals(MAX_FIRST_RECORD_WAIT_TIME, RecordWaitTimeUtil.getFirstRecordWaitTime(tooLongConfig));
  }

}
