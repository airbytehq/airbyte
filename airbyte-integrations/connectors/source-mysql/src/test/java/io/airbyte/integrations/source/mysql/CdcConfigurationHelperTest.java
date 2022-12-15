/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.helpers.CdcConfigurationHelper;
import java.util.Collections;
import java.util.Map;
import org.junit.jupiter.api.Test;

public class CdcConfigurationHelperTest {

  @Test
  void testServerTimeConfig() {
    final JsonNode emptyConfig = Jsons.jsonNode(Collections.emptyMap());
    assertDoesNotThrow(() -> CdcConfigurationHelper.checkServerTimeZoneConfig(emptyConfig));

    final JsonNode normalConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "server_time_zone", "America/Los_Angeles")));
    assertDoesNotThrow(() -> CdcConfigurationHelper.checkServerTimeZoneConfig(normalConfig));

    final JsonNode invalidConfig = Jsons.jsonNode(Map.of("replication_method",
        Map.of("method", "CDC", "server_time_zone", "CEST")));
    assertThrows(IllegalArgumentException.class, () -> CdcConfigurationHelper.checkServerTimeZoneConfig(invalidConfig));
  }

}
