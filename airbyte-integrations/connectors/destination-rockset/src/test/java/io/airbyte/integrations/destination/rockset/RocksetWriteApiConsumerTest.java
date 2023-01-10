/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.rockset;

import static io.airbyte.integrations.destination.rockset.RocksetUtils.API_KEY_ID;
import static io.airbyte.integrations.destination.rockset.RocksetUtils.API_SERVER_ID;
import static io.airbyte.integrations.destination.rockset.RocksetUtils.ROCKSET_WORKSPACE_ID;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.integrations.standardtest.destination.PerStreamStateMessageTest;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class RocksetWriteApiConsumerTest extends PerStreamStateMessageTest {

  @Mock
  private Consumer<AirbyteMessage> outputRecordCollector;

  @Mock
  private ConfiguredAirbyteCatalog catalog;

  private RocksetWriteApiConsumer consumer;

  @BeforeEach
  public void init() {
    consumer = new RocksetWriteApiConsumer(getTestConfig(), catalog, outputRecordCollector);
  }

  @Override
  protected Consumer<AirbyteMessage> getMockedConsumer() {
    return outputRecordCollector;
  }

  @Override
  protected FailureTrackingAirbyteMessageConsumer getMessageConsumer() {
    return consumer;
  }

  private JsonNode getTestConfig() {
    return Jsons.jsonNode(
        ImmutableMap.builder()
            .put(API_KEY_ID, "testApiKey")
            .put(API_SERVER_ID, "testApiServerId")
            .put(ROCKSET_WORKSPACE_ID, "testRocksetWorkspaceId")
            .build());
  }

}
