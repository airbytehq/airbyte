package io.airbyte.integrations.source.mysql;

import static io.airbyte.integrations.source.mysql.helpers.CdcConfigurationHelper.MAX_FIRST_RECORD_WAIT_TIME;
import static io.airbyte.integrations.source.mysql.helpers.CdcConfigurationHelper.MIN_FIRST_RECORD_WAIT_TIME;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.helpers.CdcConfigurationHelper;
import java.time.Duration;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

public class CdcConfigurationHelperTest {

  @Test
  void testGetFirstRecordWaitTime() {
    final JsonNode emptyConfig = Jsons.jsonNode(Collections.emptyMap());
    assertDoesNotThrow(() -> CdcConfigurationHelper.checkFirstRecordWaitTime(emptyConfig));
    assertEquals(Optional.empty(), CdcConfigurationHelper.getFirstRecordWaitSeconds(emptyConfig));
    assertEquals(CdcConfigurationHelper.DEFAULT_FIRST_RECORD_WAIT_TIME, CdcConfigurationHelper.getFirstRecordWaitTime(emptyConfig));

    final JsonNode normalConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", 500)));
    assertDoesNotThrow(() -> CdcConfigurationHelper.checkFirstRecordWaitTime(normalConfig));
    assertEquals(Optional.of(500), CdcConfigurationHelper.getFirstRecordWaitSeconds(normalConfig));
    assertEquals(Duration.ofSeconds(500), CdcConfigurationHelper.getFirstRecordWaitTime(normalConfig));

    final int tooShortTimeout = (int) MIN_FIRST_RECORD_WAIT_TIME.getSeconds() - 1;
    final JsonNode tooShortConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooShortTimeout)));
    assertThrows(IllegalArgumentException.class, () -> CdcConfigurationHelper.checkFirstRecordWaitTime(tooShortConfig));
    assertEquals(Optional.of(tooShortTimeout), CdcConfigurationHelper.getFirstRecordWaitSeconds(tooShortConfig));
    assertEquals(MIN_FIRST_RECORD_WAIT_TIME, CdcConfigurationHelper.getFirstRecordWaitTime(tooShortConfig));

    final int tooLongTimeout = (int) MAX_FIRST_RECORD_WAIT_TIME.getSeconds() + 1;
    final JsonNode tooLongConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "initial_waiting_seconds", tooLongTimeout)));
    assertThrows(IllegalArgumentException.class, () -> CdcConfigurationHelper.checkFirstRecordWaitTime(tooLongConfig));
    assertEquals(Optional.of(tooLongTimeout), CdcConfigurationHelper.getFirstRecordWaitSeconds(tooLongConfig));
    assertEquals(MAX_FIRST_RECORD_WAIT_TIME, CdcConfigurationHelper.getFirstRecordWaitTime(tooLongConfig));
  }

}
