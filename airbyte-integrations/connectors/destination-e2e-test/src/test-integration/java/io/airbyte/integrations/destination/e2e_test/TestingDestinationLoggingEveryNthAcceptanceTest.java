package io.airbyte.integrations.destination.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.e2e_test.TestingDestinations.TestDestinationType;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.Collections;
import java.util.List;
import java.util.Map;

public class TestingDestinationLoggingEveryNthAcceptanceTest extends DestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-e2e-test:dev";
  }

  @Override
  protected JsonNode getConfig() {
    final JsonNode loggingConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("logging_type", "EveryNth")
        .put("nth_entry_to_log", 1)
        .put("max_entry_count", 3)
        .build());
    return Jsons.jsonNode(Map.of("type", TestDestinationType.LOGGING.name(), "logging_config", loggingConfig));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    final JsonNode loggingConfig = Jsons.jsonNode(ImmutableMap.builder()
        .put("logging_type", "LastN")
        // max allowed entry count is 1000
        .put("max_entry_count", 3000)
        .build());
    return Jsons.jsonNode(Map.of("type", TestDestinationType.LOGGING.name(), "logging_config", loggingConfig));
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    return Collections.emptyList();
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv) {
    // do nothing
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    // do nothing
  }

  @Override
  protected void assertSameMessages(final List<AirbyteMessage> expected,
                                    final List<AirbyteRecordMessage> actual,
                                    final boolean pruneAirbyteInternalFields) {
    // do nothing
  }

}
