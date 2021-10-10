/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.destination_null;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.Collections;
import java.util.List;

public class NullDestinationAcceptanceTest extends DestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-null:dev";
  }

  @Override
  protected JsonNode getConfig() {
    final JsonNode loggingConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("logging_type", "EveryNth")
        .put("nth_entry_to_log", 1)
        .put("max_entry_count", 3)
        .build());
    return Jsons.jsonNode(Collections.singletonMap("logging", loggingConfig));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode loggingConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("logging_type", "LastN")
        .put("max_entry_count", 3000)
        .build());
    return Jsons.jsonNode(Collections.singletonMap("logging", loggingConfig));
  }

  @Override
  protected List<JsonNode> retrieveRecords(TestDestinationEnv testEnv,
                                           String streamName,
                                           String namespace,
                                           JsonNode streamSchema) {
    return Collections.emptyList();
  }

  @Override
  protected void setup(TestDestinationEnv testEnv) {
    // do nothing
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) {
    // do nothing
  }

  @Override
  protected void assertSameMessages(List<AirbyteMessage> expected, List<AirbyteRecordMessage> actual, boolean pruneAirbyteInternalFields) {
    // do nothing
  }

}
