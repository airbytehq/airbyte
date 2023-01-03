/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.standardtest.destination.DestinationAcceptanceTest;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.Collections;
import java.util.List;

public class DevNullDestinationAcceptanceTest extends DestinationAcceptanceTest {

  @Override
  protected String getImageName() {
    return "airbyte/destination-dev-null:dev";
  }

  @Override
  protected JsonNode getConfig() {
    return Jsons.jsonNode(Collections.singletonMap("type", "SILENT"));
  }

  @Override
  protected JsonNode getFailCheckConfig() {
    return Jsons.jsonNode(Collections.singletonMap("type", "invalid"));
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
    assertEquals(0, actual.size());
  }

}
