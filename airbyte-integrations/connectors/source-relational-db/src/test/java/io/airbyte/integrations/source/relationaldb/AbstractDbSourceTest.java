/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

/**
 * Test suite for the {@link AbstractDbSource} class.
 */
public class AbstractDbSourceTest {

  @Test
  void testDeserializationOfLegacyState() throws IOException {
    final AbstractDbSource dbSource = spy(AbstractDbSource.class);
    final JsonNode config = mock(JsonNode.class);

    final String legacyStateJson = MoreResources.readResource("states/legacy.json");
    final JsonNode legacyState = Jsons.deserialize(legacyStateJson);

    final List<AirbyteStateMessage> result = dbSource.deserializeInitialState(legacyState, config);
    assertEquals(1, result.size());
    assertEquals(AirbyteStateType.LEGACY, result.get(0).getType());
  }

  @Test
  void testDeserializationOfGlobalState() throws IOException {
    setEnv(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    final AbstractDbSource dbSource = spy(AbstractDbSource.class);
    final JsonNode config = mock(JsonNode.class);

    final String globalStateJson = MoreResources.readResource("states/global.json");
    final JsonNode globalState = Jsons.deserialize(globalStateJson);

    final List<AirbyteStateMessage> result = dbSource.deserializeInitialState(globalState, config);
    assertEquals(1, result.size());
    assertEquals(AirbyteStateType.GLOBAL, result.get(0).getType());
  }

  @Test
  void testDeserializationOfStreamState() throws IOException {
    setEnv(EnvVariableFeatureFlags.USE_STREAM_CAPABLE_STATE, "true");
    final AbstractDbSource dbSource = spy(AbstractDbSource.class);
    final JsonNode config = mock(JsonNode.class);

    final String streamStateJson = MoreResources.readResource("states/per_stream.json");
    final JsonNode streamState = Jsons.deserialize(streamStateJson);

    final List<AirbyteStateMessage> result = dbSource.deserializeInitialState(streamState, config);
    assertEquals(2, result.size());
    assertEquals(AirbyteStateType.STREAM, result.get(0).getType());
  }

  @Test
  void testDeserializationOfNullState() throws IOException {
    final AbstractDbSource dbSource = spy(AbstractDbSource.class);
    final JsonNode config = mock(JsonNode.class);

    final List<AirbyteStateMessage> result = dbSource.deserializeInitialState(null, config);
    assertEquals(1, result.size());
    assertEquals(dbSource.getSupportedStateType(config), result.get(0).getType());
  }

  public static void setEnv(final String key, final String value) {
    try {
      final Map<String, String> env = System.getenv();
      final Class<?> cl = env.getClass();
      final Field field = cl.getDeclaredField("m");
      field.setAccessible(true);
      final Map<String, String> writableEnv = (Map<String, String>) field.get(env);
      writableEnv.put(key, value);
    } catch (final Exception e) {
      throw new IllegalStateException("Failed to set environment variable", e);
    }
  }
}
