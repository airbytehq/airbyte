/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.relationaldb.state.StateGeneratorUtils;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.io.IOException;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables;
import uk.org.webcompere.systemstubs.jupiter.SystemStub;
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension;

/**
 * Test suite for the {@link AbstractDbSource} class.
 */
@ExtendWith(SystemStubsExtension.class)
public class AbstractDbSourceTest {

  @SystemStub
  private EnvironmentVariables environmentVariables;

  @Test
  void testDeserializationOfLegacyState() throws IOException {
    final AbstractDbSource dbSource = spy(AbstractDbSource.class);
    final JsonNode config = mock(JsonNode.class);

    final String legacyStateJson = MoreResources.readResource("states/legacy.json");
    final JsonNode legacyState = Jsons.deserialize(legacyStateJson);

    final List<AirbyteStateMessage> result = StateGeneratorUtils.deserializeInitialState(legacyState, false,
        dbSource.getSupportedStateType(config));
    assertEquals(1, result.size());
    assertEquals(AirbyteStateType.LEGACY, result.get(0).getType());
  }

  @Test
  void testDeserializationOfGlobalState() throws IOException {
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    final AbstractDbSource dbSource = spy(AbstractDbSource.class);
    final JsonNode config = mock(JsonNode.class);

    final String globalStateJson = MoreResources.readResource("states/global.json");
    final JsonNode globalState = Jsons.deserialize(globalStateJson);

    final List<AirbyteStateMessage> result =
        StateGeneratorUtils.deserializeInitialState(globalState, true, dbSource.getSupportedStateType(config));
    assertEquals(1, result.size());
    assertEquals(AirbyteStateType.GLOBAL, result.get(0).getType());
  }

  @Test
  void testDeserializationOfStreamState() throws IOException {
    environmentVariables.set(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    final AbstractDbSource dbSource = spy(AbstractDbSource.class);
    final JsonNode config = mock(JsonNode.class);

    final String streamStateJson = MoreResources.readResource("states/per_stream.json");
    final JsonNode streamState = Jsons.deserialize(streamStateJson);

    final List<AirbyteStateMessage> result =
        StateGeneratorUtils.deserializeInitialState(streamState, true, dbSource.getSupportedStateType(config));
    assertEquals(2, result.size());
    assertEquals(AirbyteStateType.STREAM, result.get(0).getType());
  }

  @Test
  void testDeserializationOfNullState() throws IOException {
    final AbstractDbSource dbSource = spy(AbstractDbSource.class);
    final JsonNode config = mock(JsonNode.class);

    final List<AirbyteStateMessage> result = StateGeneratorUtils.deserializeInitialState(null, false, dbSource.getSupportedStateType(config));
    assertEquals(1, result.size());
    assertEquals(dbSource.getSupportedStateType(config), result.get(0).getType());
  }

}
