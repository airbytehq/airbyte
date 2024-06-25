/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.e2e_test.TestingDestinations.TestDestinationType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class TestingSilentDestinationAcceptanceTest extends DestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-e2e-test:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(
        Collections.singletonMap("test_destination", Collections.singletonMap("test_destination_type", TestDestinationType.SILENT.name())));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(Collections.singletonMap("test_destination", Collections.singletonMap("test_destination_type", "invalid")));
  }

  @Override
  protected List<JsonNode> retrieveRecords(final TestDestinationEnv testEnv,
                                           final String streamName,
                                           final String namespace,
                                           final JsonNode streamSchema) {
    return Collections.emptyList();
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
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
    assertEquals(0, actual.size());
  }

  @Override
  // Skip because `retrieveRecords` returns an empty list at all times.
  @Disabled
  @Test
  public void testSyncNotFailsWithNewFields() {}

  @Override
  // This test assumes that dedup support means normalization support.
  // Override it to do nothing.
  @Disabled
  @Test
  public void testIncrementalDedupeSync() throws Exception {
    super.testIncrementalDedupeSync();
  }

}
