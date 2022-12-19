/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.workers.test_utils.TestConfigHelpers;
import java.util.Map;
import org.apache.commons.lang3.tuple.ImmutablePair;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class WorkerUtilsTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerUtilsTest.class);

  @Test
  void testMapStreamNamesToSchemasWithNullNamespace() {
    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig();
    final StandardSyncInput syncInput = syncPair.getValue();
    final Map<AirbyteStreamNameNamespacePair, JsonNode> mapOutput = WorkerUtils.mapStreamNamesToSchemas(syncInput);
    assertNotNull(mapOutput.get(new AirbyteStreamNameNamespacePair("user_preferences", null)));
  }

  @Test
  void testMapStreamNamesToSchemasWithMultipleNamespaces() {
    final ImmutablePair<StandardSync, StandardSyncInput> syncPair = TestConfigHelpers.createSyncConfig(true);
    final StandardSyncInput syncInput = syncPair.getValue();
    final Map<AirbyteStreamNameNamespacePair, JsonNode> mapOutput = WorkerUtils.mapStreamNamesToSchemas(syncInput);
    assertNotNull(mapOutput.get(new AirbyteStreamNameNamespacePair("user_preferences", "namespace")));
    assertNotNull(mapOutput.get(new AirbyteStreamNameNamespacePair("user_preferences", "namespace2")));
  }

}
